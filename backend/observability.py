"""Allowlisted telemetry: never serialize request/exception/provider payloads."""
import time
import json
import logging
import re
from pathlib import Path
from logging.handlers import RotatingFileHandler
from contextvars import ContextVar
from functools import wraps
import uuid
from contextlib import contextmanager
import sentry_sdk
from sentry_sdk import logger as sentry_logger

local_logger = logging.getLogger('beprogram.lifecycle')
local_logger.propagate = False
local_logger.setLevel(logging.INFO)
OPERATIONS = {'change_filter_and_question', 'answer_evaluation_and_persistence', 'gate_reconciliation',
              'managed_ask', 'checkpoint_explanation', 'practice_question', 'pr_import', 'pr_publication', 'receipt_issuance', 'speech_playback', 'transcription', 'evaluation', 'local_inference'}
CATEGORIES = {'none', 'unexpected', 'invalid_local_response', 'ungrounded_local_pass', 'local_model_timeout',
              'rate_limited', 'operation_busy', 'invalid_assessment', 'invalid_evaluation', 'stale_version',
              'unauthorized', 'gate_locked', 'context_expired', 'not_answerable', 'not_found',
              'idempotency_conflict', 'model_missing', 'local_model_unavailable', 'local_context_too_large',
              'ask_context_changed', 'invalid_assistant_response'}
active_correlation = ContextVar('beprogram_correlation', default=None)


def measured(operation):
    def decorate(function):
        @wraps(function)
        def wrapped(*args, **kwargs):
            with stage(operation):
                return function(*args, **kwargs)
        return wrapped
    return decorate


def local_event(operation, correlation_id, status, duration_ms, category):
    # Fixed fields only: never serialize an exception, request or model response.
    correlation = correlation_id if isinstance(correlation_id, str) and re.fullmatch(r'[0-9a-f-]{36}', correlation_id) else 'redacted'
    event = {'time': round(time.time(), 3), 'operation': operation if operation in OPERATIONS else 'other',
             'correlation_id': correlation, 'status': status if status in {'ok', 'error'} else 'error',
             'duration_ms': max(0, int(duration_ms)), 'category': category if category in CATEGORIES else 'other'}
    try:
        local_logger.info(json.dumps(event, separators=(',', ':')))
    except Exception:
        pass


def scrub_event(event, hint=None):
    return {'event_id': event.get('event_id'), 'timestamp': event.get('timestamp'), 'level': event.get('level', 'error'),
            'message': 'BeProgram operational failure', 'tags': {k: v for k, v in event.get('tags', {}).items() if k in ('operation', 'category', 'correlation_id')}}


def scrub_transaction(event, hint=None):
    event.pop('request', None)
    event.pop('user', None)
    event.pop('extra', None)
    event.pop('breadcrumbs', None)
    for span in event.get('spans', []):
        span.pop('data', None)
    return event


def scrub_log(log, hint=None):
    log['body'] = 'BeProgram lifecycle'
    log['attributes'] = {k: v for k, v in log.get('attributes', {}).items() if k in ('operation', 'status', 'duration_ms', 'correlation_id', 'category') or k.startswith('sentry.')}
    return log


def configure(config):
    # Empty DSN explicitly ignores legacy SENTRY_DSN environment configuration.
    sentry_sdk.init(dsn='', default_integrations=False, auto_enabling_integrations=False)
    for handler in list(local_logger.handlers):
        local_logger.removeHandler(handler)
        handler.close()
    local_logger.addHandler(logging.NullHandler())
    if config.local_logs_enabled and config.environment != 'test':
        try:
            path = Path(config.local_log_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            handler = RotatingFileHandler(path, maxBytes=1_000_000, backupCount=3, encoding='utf-8')
            handler.setFormatter(logging.Formatter('%(message)s'))
            local_logger.addHandler(handler)
        except OSError:
            pass  # Local disk/logging failure must not stop the learning flow.


@contextmanager
def stage(operation, correlation_id=None):
    correlation_id = correlation_id or active_correlation.get() or str(uuid.uuid4())
    token = active_correlation.set(correlation_id)
    start, status, category = time.monotonic(), 'ok', 'none'
    with sentry_sdk.new_scope() as lifecycle_scope, sentry_sdk.start_transaction(op='beprogram.' + operation, name=operation) as transaction:
        lifecycle_scope.set_tag('correlation_id', correlation_id)
        transaction.set_tag('correlation_id', correlation_id)
        try:
            yield
        except Exception as exc:
            status = 'error'
            category = getattr(exc, 'code', 'unexpected')
            with sentry_sdk.new_scope() as scope:
                scope.set_tag('operation', operation)
                scope.set_tag('category', getattr(exc, 'code', 'unexpected'))
                sentry_sdk.capture_message('BeProgram operational failure', level='error')
            raise
        finally:
            active_correlation.reset(token)
            local_event(operation, correlation_id, status, int((time.monotonic()-start)*1000), category)
            try:
                sentry_logger.info('BeProgram lifecycle', attributes={'operation': operation, 'status': status,
                    'duration_ms': int((time.monotonic()-start)*1000), 'correlation_id': correlation_id})
            except Exception:
                pass  # Telemetry must never turn a persisted result into an API failure.
