import json
import sentry_sdk
from sentry_sdk import logger
from sentry_sdk.transport import Transport
import pytest
from pydantic import ValidationError
from backend.config import Settings
from backend import observability as obs
from backend.errors import AppError


class Memory(Transport):
    def __init__(self):
        super().__init__(); self.envelopes = []

    def capture_envelope(self, envelope):
        self.envelopes.append(envelope)


def test_dsn_alone_never_enables_telemetry():
    transport = Memory()
    obs.configure(Settings(_env_file=None, environment='test', sentry_dsn='https://public@example.test/1'), transport)
    with obs.stage('evaluation'):
        pass
    sentry_sdk.flush(timeout=2)
    assert not transport.envelopes


def test_optin_emits_correlated_nested_trace_logs_without_private_metadata():
    transport = Memory()
    obs.configure(Settings(_env_file=None, environment='test', sentry_enabled=True,
        sentry_dsn='https://public@o0.ingest.us.sentry.io/1'), transport)
    try:
        with pytest.raises(AppError), obs.stage('managed_ask'):
            sentry_sdk.set_context('private', {'source':'PRIVATE_SOURCE'})
            sentry_sdk.set_user({'id':'PRIVATE_USER'})
            with obs.stage('local_inference'):
                logger.info('PRIVATE_LOG', attributes={'sentry.private':'PRIVATE_META', 'operation':'PRIVATE_PATH'})
                raise AppError('local_model_timeout', 'PRIVATE_ERROR_TOKEN', 503)
        sentry_sdk.flush(timeout=2)
        wire = b'\n'.join(e.serialize() for e in transport.envelopes).decode()
        assert 'PRIVATE_' not in wire
        items = [item for env in transport.envelopes for item in env.items]
        transactions = [i.payload.json for i in items if i.type == 'transaction']
        assert len(transactions) == 1
        assert transactions[0]['transaction'] == 'managed_ask'
        assert any(s['op'] == 'beprogram.local_inference' for s in transactions[0]['spans'])
        assert any(i.type == 'log' for i in items)
        assert 'local_model_timeout' in wire
        assert 'request' not in transactions[0] and 'server_name' not in transactions[0]
    finally:
        sentry_sdk.get_client().close()
        obs.configure(Settings(_env_file=None, environment='test'))


@pytest.mark.parametrize('dsn', ['', 'http://public@o0.ingest.sentry.io/1', 'https://public@evil.test/1'])
def test_enabled_sentry_rejects_unconfigured_or_non_sentry_destination(dsn):
    with pytest.raises(ValidationError):
        Settings(_env_file=None, sentry_enabled=True, sentry_dsn=dsn)
