import base64
import json
from copy import deepcopy
from nacl.signing import SigningKey
from solders.keypair import Keypair
from solders.hash import Hash
from solders.pubkey import Pubkey
from solders.transaction import Transaction
from backend.receipts import ReceiptService, WalletInput, PreviewInput, IssueInput, verify_package, MEMO, DEVNET_GENESIS
from backend.errors import AppError
from backend.context import digest
from tests.conftest import start, change, answer, GOOD
import pytest


def test_disabled_receipt_routes_never_contact_rpc(app_env, monkeypatch):
    from backend.receipts import RPC
    client, _, _, _, config = app_env
    assert config.solana_enabled is False
    def forbidden(*args, **kwargs):
        pytest.fail('Disabled receipts must not contact Solana')
    monkeypatch.setattr(RPC, 'call', forbidden)
    for method, route, body in [
        ('POST', '/v1/verify', {'manifest': {}, 'signature': 'a' * 88}),
        ('POST', '/v1/receipts/old-record/reconcile', None),
        ('GET', '/v1/receipts/old-record', None),
    ]:
        response = client.request(method, route, json=body)
        assert response.status_code == 503
        assert response.json()['code'] == 'receipts_disabled'
    assert client.get('/v1/config').json()['capabilities']['receipts'] is False


class FixtureRPC:
    timeout = False
    sends = 0
    signed = None
    status = None
    transaction = None

    def check_network(self):
        return None

    def call(self, method, params=None):
        if method == 'getLatestBlockhash':
            return {'value': {'blockhash': str(Hash.default()), 'lastValidBlockHeight': 1000}}
        if method == 'sendTransaction':
            self.sends += 1
            tx = Transaction.from_bytes(base64.b64decode(params[0]))
            self.signed = tx
            if self.timeout:
                raise AppError('rpc_unavailable', 'Simulated ambiguous broadcast', 503, True)
            return str(tx.signatures[0])
        if method == 'getSignatureStatuses':
            return {'value': [self.status]}
        if method == 'getBlockHeight':
            return 999
        if method == 'getTransaction':
            return self.transaction
        raise AssertionError(method)


def setup_receipt(app_env):
    c, app, _, _, config = app_env
    _, s = start(c)
    cp = answer(c, change(c, s).json()['checkpoint'], GOOD).json()
    issuer = Keypair()
    config.solana_enabled = True
    config.solana_issuer_key = json.dumps(list(bytes(issuer)))
    wallet = SigningKey.generate()
    subject = str(Pubkey.from_bytes(bytes(wallet.verify_key)))
    rpc = FixtureRPC()
    service = ReceiptService(app.state.service, config, rpc)
    challenge = service.challenge('local-developer', WalletInput(checkpoint_id=cp['id'], subject=subject))
    signature = base64.b64encode(wallet.sign(challenge['message'].encode()).signature).decode()
    inp = PreviewInput(checkpoint_id=cp['id'], subject=subject, challenge_id=challenge['challenge_id'], signature=signature)
    preview = service.preview('local-developer', inp)
    return service, rpc, preview, inp, issuer, c, s


def test_wallet_replay_and_issuance_timeout_deduplication(app_env):
    service, rpc, preview, inp, issuer, client, session = setup_receipt(app_env)
    with pytest.raises(AppError, match='challenge_invalid'):
        service.preview('local-developer', inp)
    rpc.timeout = True
    issued = service.issue('local-developer', IssueInput(preview_id=preview['id'], approved_digest=preview['digest'], consent=True))
    assert issued['state'] == 'pending_confirmation'
    first_signature = issued['signature']
    assert rpc.signed.verify_with_results() == [True]
    rpc.timeout = False
    rpc.status = {'err': None, 'confirmationStatus': 'confirmed'}
    result = service.issue('local-developer', IssueInput(preview_id=preview['id'], approved_digest=preview['digest'], consent=True))
    assert result['signature'] == first_signature and result['state'] == 'confirmed'
    assert rpc.sends == 1
    assert client.get(f"/v1/sessions/{session['id']}/gate").json()['available']


def test_independent_verifier_tamper_issuer_subject_limits(app_env):
    service, rpc, preview, _, issuer, _, _ = setup_receipt(app_env)
    package = service.get('local-developer', preview['id'], export=True)
    manifest = package['manifest']
    rpc.transaction = {'meta': {'err': None}, 'transaction': {'message': {
        'accountKeys': [{'pubkey': str(issuer.pubkey()), 'signer': True}],
        'instructions': [{'programId': MEMO, 'parsed': preview['public_memo']}]}}}
    verified = verify_package(manifest, 'fixture-signature', rpc, [str(issuer.pubkey())])
    assert verified['issuer_verified'] and verified['evidence_matches']
    assert not verified['subject_control_verified']
    assert 'not supported' in verified['revocation']
    tampered = deepcopy(manifest); tampered['concept'] = 'Different concept'
    assert verify_package(tampered, 'fixture-signature', rpc, [str(issuer.pubkey())])['status'] == 'evidence_mismatch'
    assert verify_package(manifest, 'fixture-signature', rpc, ['another-issuer'])['status'] == 'unknown_issuer'
    rpc.transaction['transaction']['message']['accountKeys'][0]['signer'] = False
    assert verify_package(manifest, 'fixture-signature', rpc, [str(issuer.pubkey())])['status'] == 'unknown_issuer'


def test_receipt_digest_consent_and_owner_binding(app_env):
    service, rpc, preview, _, _, _, _ = setup_receipt(app_env)
    with pytest.raises(AppError, match='preview_mismatch'):
        service.issue('local-developer', IssueInput(preview_id=preview['id'], approved_digest='0'*64, consent=True))
    with pytest.raises(AppError, match='not_found'):
        service.get('other-owner', preview['id'], export=True)
    assert rpc.sends == 0
