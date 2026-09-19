import json
import time
from types import SimpleNamespace
import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from starlette.requests import Request
from backend.auth import Auth
from backend.config import Settings
from backend.errors import AppError
from backend.observability import scrub_event, scrub_transaction, scrub_log, stage
import sentry_sdk
from sentry_sdk.transport import Transport


def test_supabase_signature_issuer_audience_expiry_and_role():
    key=rsa.generate_private_key(public_exponent=65537,key_size=2048)
    auth=Auth(Settings(_env_file=None,supabase_url='https://auth.example.test'))
    auth.jwks=SimpleNamespace(get_signing_key_from_jwt=lambda token:SimpleNamespace(key=key.public_key()))
    claims={'sub':'user-1','iss':'https://auth.example.test/auth/v1','aud':'authenticated','iat':int(time.time()),'exp':int(time.time())+60,'role':'authenticated'}
    def request(payload, signing=key):
        token=jwt.encode(payload,signing,algorithm='RS256')
        return Request({'type':'http','headers':[(b'authorization',('Bearer '+token).encode())],'client':('127.0.0.1',1234)})
    assert auth(request(claims))=='user-1'
    for update in [{'iss':'https://attacker.test'},{'aud':'other-app'},{'exp':1},{'role':'service_role'}]:
        with pytest.raises(AppError,match='unauthorized'):
            auth(request({**claims,**update}))
    with pytest.raises(AppError,match='unauthorized'):
        auth(request(claims,rsa.generate_private_key(public_exponent=65537,key_size=2048)))


def test_actual_sentry_envelopes_redact_sensitive_payloads():
    class Memory(Transport):
        envelopes=[]
        def capture_envelope(self,envelope):
            self.envelopes.append(envelope)
    transport=Memory()
    client=sentry_sdk.Client(dsn='https://public@example.test/1',transport=transport,default_integrations=False,
        auto_enabling_integrations=False,enable_logs=True,traces_sample_rate=1.0,
        before_send=scrub_event,before_send_transaction=scrub_transaction,before_send_log=scrub_log)
    old=sentry_sdk.get_client()
    try:
        sentry_sdk.get_global_scope().set_client(client)
        correlation = 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee'
        with stage('evaluation',correlation):
            sentry_sdk.capture_event({'level':'error','message':'PRIVATE_CODE_SECRET','request':{'data':'PRIVATE_ANSWER_SECRET'},'extra':{'token':'PRIVATE_TOKEN_SECRET'}})
        client.flush(timeout=2)
        serialized=b'\n'.join(e.serialize() for e in transport.envelopes).decode()
        assert 'PRIVATE_CODE_SECRET' not in serialized and 'PRIVATE_ANSWER_SECRET' not in serialized and 'PRIVATE_TOKEN_SECRET' not in serialized
        assert correlation in serialized
        # Correlation survives independently in error, trace and lifecycle log payloads.
        assert serialized.count(correlation) >= 3
        assert 'transaction' in serialized and 'log' in serialized and 'CodeProof operational failure' in serialized
    finally:
        sentry_sdk.get_global_scope().set_client(old)
        client.close()
