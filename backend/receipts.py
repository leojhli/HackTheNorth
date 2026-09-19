"""Optional issuer-signed Devnet Memo receipts; no credential/revocation claims."""
import base64
import json
import secrets
import time
from typing import Literal
import httpx
from nacl.signing import VerifyKey
from pydantic import Field
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.hash import Hash
from solders.instruction import Instruction, AccountMeta
from solders.transaction import Transaction
from sqlalchemy import select
from .contracts import Strict
from .context import digest
from .db import Checkpoint, Operation, uid
from .service import owned, PASSING, record
from .errors import AppError

MEMO = 'MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr'
DEVNET_GENESIS = 'EtWTRABZaYq6iMfeYKouRu166VU2xqa1'


class WalletInput(Strict):
    checkpoint_id: str
    subject: str = Field(min_length=32, max_length=44)


class PreviewInput(WalletInput):
    challenge_id: str
    signature: str = Field(max_length=128)


class IssueInput(Strict):
    preview_id: str
    approved_digest: str = Field(pattern=r'^[a-f0-9]{64}$')
    consent: Literal[True]


class VerifyInput(Strict):
    manifest: dict
    signature: str = Field(min_length=64, max_length=100)


class RPC:
    def __init__(self, url):
        self.url = url

    def call(self, method, params=None):
        try:
            r = httpx.post(self.url, json={'jsonrpc': '2.0', 'id': 1, 'method': method, 'params': params or []}, timeout=15)
            r.raise_for_status()
            value = r.json()
            if 'error' in value:
                raise ValueError('RPC rejected request')
            return value['result']
        except Exception:
            raise AppError('rpc_unavailable', 'Devnet RPC is temporarily unavailable. Reconcile the existing receipt before retrying.', 503, True) from None

    def check_network(self):
        if self.call('getGenesisHash') != DEVNET_GENESIS:
            raise AppError('wrong_network', 'This endpoint is not Solana Devnet.', 409)


def memo_text(commitment):
    return 'beprogram:v1:' + commitment


def verify_package(manifest, signature, rpc, trusted_issuers):
    """Independent: uses supplied evidence + trusted RPC, never CodeProof database state."""
    base = {'network': 'Solana Devnet — demo network', 'revocation': 'Revocation not supported in this prototype',
            'subject_control_verified': False, 'subject_note': 'Possession of a package does not prove current wallet control.'}
    if manifest.get('schema') != 'beprogram.assessment.v1' or manifest.get('network') != 'devnet':
        return {**base, 'status': 'evidence_mismatch', 'issuer_verified': False, 'evidence_matches': False}
    issuer = manifest.get('issuer')
    if issuer not in trusted_issuers:
        return {**base, 'status': 'unknown_issuer', 'issuer_verified': False, 'evidence_matches': False}
    try:
        rpc.check_network()
        transaction = rpc.call('getTransaction', [signature, {'encoding': 'jsonParsed', 'commitment': 'confirmed', 'maxSupportedTransactionVersion': 0}])
        if not transaction:
            return {**base, 'status': 'temporarily_unavailable', 'issuer_verified': False, 'evidence_matches': False}
        if transaction.get('meta', {}).get('err') is not None:
            return {**base, 'status': 'evidence_mismatch', 'issuer_verified': False, 'evidence_matches': False}
        message = transaction['transaction']['message']
        signer = any(k.get('pubkey') == issuer and k.get('signer') is True for k in message['accountKeys'])
        memo = any(i.get('programId') == MEMO and i.get('parsed') == memo_text(digest(manifest)) for i in message['instructions'])
        if not signer:
            return {**base, 'status': 'unknown_issuer', 'issuer_verified': False, 'evidence_matches': memo}
        expires = manifest.get('expires_at')
        status = 'evidence_matches' if memo else 'evidence_mismatch'
        if memo and expires is not None and (not isinstance(expires, int) or expires < time.time()):
            status = 'expired'
        return {**base, 'status': status, 'issuer_verified': signer, 'evidence_matches': memo, 'subject': manifest.get('subject'), 'signature': signature}
    except AppError:
        return {**base, 'status': 'temporarily_unavailable', 'issuer_verified': False, 'evidence_matches': False}
    except (ValueError, TypeError, KeyError):
        return {**base, 'status': 'evidence_mismatch', 'issuer_verified': False, 'evidence_matches': False}


class ReceiptService:
    def __init__(self, service, config, rpc=None):
        self.core, self.config = service, config
        self.database = service.database
        self.rpc = rpc or RPC(config.solana_rpc_url)

    def issuer(self):
        if not self.config.solana_enabled or not self.config.solana_issuer_key:
            raise AppError('receipts_unconfigured', 'Devnet receipts are not configured.', 503)
        try:
            return Keypair.from_bytes(bytes(json.loads(self.config.solana_issuer_key)))
        except Exception:
            raise AppError('issuer_unavailable', 'The server issuer configuration is invalid.', 503) from None

    def challenge(self, owner, data):
        self.issuer()
        try:
            Pubkey.from_string(data.subject)
        except ValueError:
            raise AppError('invalid_wallet', 'Enter a valid Solana test wallet public key.') from None
        with self.core.serial(owner), self.database.transaction() as db:
            cp = owned(db, Checkpoint, data.checkpoint_id, owner)
            if cp.status not in PASSING:
                raise AppError('not_passed', 'Only a persisted passing checkpoint is eligible.', 409)
            expires, challenge_id, nonce = int(time.time())+300, uid(), secrets.token_hex(24)
            message = '\n'.join(['CodeProof assessment receipt', f'Domain: {self.config.app_origin}', f'Checkpoint: {cp.id}',
                f'Subject: {data.subject}', f'Nonce: {nonce}', f'Expires: {expires}', 'This proves wallet control for this private receipt preview. No funds are requested.'])
            op = Operation(id=challenge_id, owner=owner, project_id=cp.project_id, kind='wallet_challenge', key=challenge_id,
                state='fresh', payload={'checkpoint_id': cp.id, 'subject': data.subject, 'expires': expires, 'message': message})
            db.add(op)
            return {'challenge_id': challenge_id, 'message': message, 'expires_at': expires}

    def preview(self, owner, data):
        issuer = self.issuer()
        with self.core.serial(owner), self.database.transaction() as db:
            challenge = owned(db, Operation, data.challenge_id, owner)
            c = challenge.payload
            if challenge.kind != 'wallet_challenge' or challenge.state != 'fresh' or c['expires'] < time.time() or c['checkpoint_id'] != data.checkpoint_id or c['subject'] != data.subject:
                raise AppError('challenge_invalid', 'Wallet challenge is expired, reused, or does not match this receipt.', 409)
            try:
                VerifyKey(bytes(Pubkey.from_string(data.subject))).verify(c['message'].encode(), base64.b64decode(data.signature, validate=True))
            except Exception:
                raise AppError('wallet_rejected', 'Wallet signature did not verify. Request a fresh challenge.', 403) from None
            cp = owned(db, Checkpoint, data.checkpoint_id, owner)
            if cp.status not in PASSING or not cp.snapshot.get('files'):
                raise AppError('not_eligible', 'A passing checkpoint with unexpired evidence is required.', 409)
            key = digest({'checkpoint': cp.id, 'version': cp.version, 'subject': data.subject, 'schema': 'v1'})
            existing = db.scalar(select(Operation).where(Operation.owner == owner, Operation.kind == 'receipt', Operation.key == key))
            challenge.state = 'used'
            if existing:
                if existing.state == 'awaiting_consent':
                    existing.payload = {**existing.payload, 'preview_expires': int(time.time())+600}
                return self.public(existing)
            detail = self.core.detail(db, cp)
            manifest = {'schema': 'beprogram.assessment.v1', 'receipt_id': uid(), 'network': 'devnet', 'subject': data.subject,
                'issuer': str(issuer.pubkey()), 'snapshot_digest': cp.snapshot_hash, 'checkpoint_version': cp.version,
                'concept': cp.question['concept'], 'rubric_version': 'v1', 'model': cp.model,
                'assistance_level': 'assisted' if cp.status == 'passed_with_help' else 'unaided', 'assessed_at': int(cp.passed_at),
                'expires_at': None, 'nonce': secrets.token_hex(32),
                'evidence': {'snapshot': cp.snapshot, 'question': cp.question, 'attempts': [{'answer': a['answer'], 'evaluation': a['evaluation']} for a in detail['attempts'] if a['state'] == 'completed']}}
            commitment = digest(manifest)
            op = Operation(owner=owner, project_id=cp.project_id, kind='receipt', key=key, state='awaiting_consent',
                payload={'manifest': manifest, 'digest': commitment, 'checkpoint_id': cp.id, 'preview_expires': int(time.time())+600,
                         'public_memo': memo_text(commitment)}, result={})
            db.add(op); db.flush()
            return self.public(op)

    def public(self, op):
        result = op.result or {}
        return {'id': op.id, 'state': op.state, 'digest': op.payload['digest'], 'public_memo': op.payload['public_memo'],
            'issuer': op.payload['manifest']['issuer'] if op.payload.get('manifest') else None,
            'subject': op.payload['manifest']['subject'] if op.payload.get('manifest') else None,
            'network': 'Solana Devnet — demo network', 'signature': result.get('signature'),
            'revocation': 'Revocation not supported in this prototype',
            'disclosure': 'Only this memo and issuer transaction metadata go on-chain. The private export contains captured code, questions and submitted explanations. Publication cannot be recalled; Devnet may reset.'}

    def get(self, owner, id, export=False):
        with self.database.transaction() as db:
            op = owned(db, Operation, id, owner)
            if op.kind != 'receipt':
                raise AppError('not_found', 'Receipt not found.', 404)
            if export:
                if not op.payload.get('manifest'):
                    raise AppError('evidence_expired', 'The private evidence package has expired.', 410)
                return {'manifest': op.payload['manifest'], 'signature': (op.result or {}).get('signature'), 'network': 'devnet'}
            return self.public(op)

    def issue(self, owner, data):
        issuer = self.issuer()
        with self.core.serial(owner) as lease:
            with self.database.transaction() as db:
                op = owned(db, Operation, data.preview_id, owner)
                if op.kind != 'receipt' or data.approved_digest != op.payload.get('digest'):
                    raise AppError('preview_mismatch', 'Approve the exact current receipt preview.', 409)
                if op.state == 'confirmed':
                    return self.public(op)
                if op.state == 'awaiting_consent' and op.payload['preview_expires'] < time.time():
                    raise AppError('preview_expired', 'This preview expired. Request a new wallet challenge and preview.', 409)
                known = op.result or {}
                manifest = op.payload['manifest']
                if not manifest or str(issuer.pubkey()) != manifest['issuer']:
                    raise AppError('issuer_changed', 'Issuer changed or evidence expired. This preview cannot be submitted.', 409)
            self.rpc.check_network()
            if known.get('signature'):
                return self.reconcile(owner, op.id)
            latest = self.rpc.call('getLatestBlockhash', [{'commitment': 'confirmed'}])['value']
            instruction = Instruction(Pubkey.from_string(MEMO), op.payload['public_memo'].encode(), [AccountMeta(issuer.pubkey(), True, False)])
            tx = Transaction.new_signed_with_payer([instruction], issuer.pubkey(), [issuer], Hash.from_string(latest['blockhash']))
            signed = base64.b64encode(bytes(tx)).decode()
            signature = str(tx.signatures[0])
            # Durable signed bytes and signature are committed BEFORE any broadcast.
            with self.database.transaction() as db:
                self.core.verify_lease(db, owner, lease)
                row = owned(db, Operation, op.id, owner)
                row.state = 'submitting'
                row.result = {'signature': signature, 'signed_transaction': signed, 'last_valid_block_height': latest['lastValidBlockHeight']}
            try:
                returned = self.rpc.call('sendTransaction', [signed, {'encoding': 'base64', 'skipPreflight': False, 'maxRetries': 0}])
                if returned != signature:
                    raise AppError('rpc_mismatch', 'RPC returned an unexpected signature. Reconcile the recorded transaction.', 503, True)
            except AppError:
                with self.database.transaction() as db:
                    row = owned(db, Operation, op.id, owner); row.state = 'pending_confirmation'
                return self.get(owner, op.id)
            return self.reconcile(owner, op.id)

    def reconcile(self, owner, id):
        with self.database.transaction() as db:
            op = owned(db, Operation, id, owner)
            if op.kind != 'receipt' or not (op.result or {}).get('signature'):
                raise AppError('not_submitted', 'This receipt has no recorded transaction.', 409)
            known = op.result
        self.rpc.check_network()
        status = self.rpc.call('getSignatureStatuses', [[known['signature']], {'searchTransactionHistory': True}])['value'][0]
        if status and status.get('err'):
            state = 'failed'
        elif status and status.get('confirmationStatus') in ('confirmed', 'finalized'):
            state = 'confirmed'
        elif self.rpc.call('getBlockHeight', [{'commitment': 'confirmed'}]) > known['last_valid_block_height']:
            state = 'expired'
        else:
            state = 'pending_confirmation'
            # Rebroadcast only identical signed bytes: Solana deduplicates the same signature.
            self.rpc.call('sendTransaction', [known['signed_transaction'], {'encoding': 'base64', 'skipPreflight': False, 'maxRetries': 0}])
        with self.database.transaction() as db:
            row = owned(db, Operation, id, owner); row.state = state
            return self.public(row)
