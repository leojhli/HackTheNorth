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
              'managed_ask', 'checkpoint_explanation', 'practice_question', 'pr_import', 'pr_publication', 'receipt_issuance', 'speech_playback', 'transcription', 'evaluation', 'local_inference', 'context_selection', 'context_read'}
CATEGORIES = {'none', 'unexpected', 'invalid_local_response', 'ungrounded_local_pass', 'local_model_timeout',
              'rate_limited', 'operation_busy', 'invalid_assessment', 'invalid_evaluation', 'stale_version',
              'unauthorized', 'gate_locked', 'context_expired', 'not_answerable', 'not_found',
              'idempotency_conflict', 'model_missing', 'local_model_unavailable', 'local_context_too_large',
              'ask_context_changed', 'invalid_assistant_response', 'invalid_context_action', 'context_review_limit'}
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


def safe_correlation(value):
    return value if isinstance(value, str) and re.fullmatch(r'[0-9a-f-]{36}', value) else 'redacted'


def safe_tags(values):
    return {'operation': values.get('operation') if values.get('operation') in OPERATIONS else 'other',
            'category': values.get('category') if values.get('category') in CATEGORIES else 'other',
            'correlation_id': safe_correlation(values.get('correlation_id'))}


def safe_trace(values):
    result = {k: v for k, v in values.items() if k in ('trace_id', 'span_id', 'parent_span_id')
              and isinstance(v, str) and re.fullmatch(r'[0-9a-f]{16}|[0-9a-f]{32}', v)}
    result['op'] = values.get('op') if values.get('op') in {'beprogram.' + op for op in OPERATIONS} else 'beprogram.other'
    if values.get('status') in {'ok', 'internal_error', 'unknown_error'}:
        result['status'] = values['status']
    return result


def scrub_event(event, hint=None):
    return {'event_id': event.get('event_id'), 'timestamp': event.get('timestamp'), 'level': 'error',
            'message': 'BeProgram operational failure', 'tags': safe_tags(event.get('tags', {})),
            'contexts': {'trace': safe_trace(event.get('contexts', {}).get('trace', {}))}}


def scrub_transaction(event, hint=None):
    # Rebuild, rather than blacklist: SDK additions must not leak local paths,
    # hostname, SQL, source, exception strings, or arbitrary custom metadata.
    def timing(values):
        return {k: v for k, v in values.items() if k in ('start_timestamp', 'timestamp')}
    return {'type': 'transaction', 'event_id': event.get('event_id'), **timing(event),
            'transaction': event.get('transaction') if event.get('transaction') in OPERATIONS else 'other',
            'contexts': {'trace': safe_trace(event.get('contexts', {}).get('trace', {}))},
            'tags': safe_tags(event.get('tags', {})),
            'spans': [{**safe_trace(s), **timing(s)} for s in event.get('spans', [])]}


def scrub_log(log, hint=None):
    log['body'] = 'BeProgram lifecycle'
    attributes = log.get('attributes', {})
    duration = attributes.get('duration_ms', 0)
    log['attributes'] = {**safe_tags(attributes),
        'status': attributes.get('status') if attributes.get('status') in {'ok', 'error'} else 'error',
        'duration_ms': max(0, int(duration)) if isinstance(duration, (int, float)) else 0}
    return log


def configure(config, transport=None):
    # A legacy DSN alone never opts in. No automatic HTTP/SQL/logging integrations.
    sentry_sdk.init(dsn=config.sentry_dsn if config.sentry_enabled else '',
        default_integrations=False, auto_enabling_integrations=False, transport=transport if config.sentry_enabled else None,
        send_default_pii=False, max_breadcrumbs=0, include_local_variables=False,
        enable_logs=config.sentry_enabled, traces_sample_rate=1.0 if config.sentry_enabled else 0.0,
        before_send=scrub_event, before_send_transaction=scrub_transaction, before_send_log=scrub_log,
        server_name='beprogram-local', environment='local', release='beprogram-backend-track-preview',
        send_client_reports=False)
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
    operation = operation if operation in OPERATIONS else 'other'
    parent = active_correlation.get()
    correlation_id = safe_correlation(correlation_id or parent or str(uuid.uuid4()))
    token = active_correlation.set(correlation_id)
    start, status, category = time.monotonic(), 'ok', 'none'
    # Nested inference appears inside the parent operation's trace, rather than
    # becoming an unrelated transaction. This makes slow model calls diagnosable.
    with sentry_sdk.new_scope() as lifecycle_scope, (sentry_sdk.start_span(op='beprogram.' + operation) if parent else sentry_sdk.start_transaction(op='beprogram.' + operation, name=operation)) as transaction:
        lifecycle_scope.set_tag('correlation_id', correlation_id)
        lifecycle_scope.set_tag('operation', operation)
        transaction.set_tag('correlation_id', correlation_id)
        transaction.set_tag('operation', operation)
        try:
            yield
        except Exception as exc:
            status = 'error'
            raw_category = getattr(exc, 'code', 'unexpected')
            category = raw_category if raw_category in CATEGORIES else 'unexpected'
            transaction.set_status('internal_error')
            transaction.set_tag('category', category)
            with sentry_sdk.new_scope() as scope:
                scope.set_tag('operation', operation)
                scope.set_tag('category', category)
                sentry_sdk.capture_message('BeProgram operational failure', level='error')
            raise
        finally:
            active_correlation.reset(token)
            local_event(operation, correlation_id, status, int((time.monotonic()-start)*1000), category)
            try:
                sentry_logger.info('BeProgram lifecycle', attributes={'operation': operation, 'status': status,
                    'duration_ms': int((time.monotonic()-start)*1000), 'correlation_id': correlation_id, 'category': category})
            except Exception:
                pass  # Telemetry must never turn a persisted result into an API failure.
