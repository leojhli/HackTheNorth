"""Allowlisted telemetry: never serialize request/exception/provider payloads."""
import time
from contextlib import contextmanager
import sentry_sdk
from sentry_sdk import logger as sentry_logger


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


@contextmanager
def stage(operation, correlation_id):
    start, status = time.monotonic(), 'ok'
    with sentry_sdk.new_scope() as lifecycle_scope, sentry_sdk.start_transaction(op='beprogram.' + operation, name=operation) as transaction:
        lifecycle_scope.set_tag('correlation_id', correlation_id)
        transaction.set_tag('correlation_id', correlation_id)
        try:
            yield
        except Exception as exc:
            status = 'error'
            with sentry_sdk.new_scope() as scope:
                scope.set_tag('operation', operation)
                scope.set_tag('category', getattr(exc, 'code', 'unexpected'))
                sentry_sdk.capture_message('BeProgram operational failure', level='error')
            raise
        finally:
            try:
                sentry_logger.info('BeProgram lifecycle', attributes={'operation': operation, 'status': status,
                    'duration_ms': int((time.monotonic()-start)*1000), 'correlation_id': correlation_id})
            except Exception:
                pass  # Telemetry must never turn a persisted result into an API failure.
