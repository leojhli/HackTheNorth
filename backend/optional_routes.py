from fastapi import Depends, UploadFile, File, Form, Response
from pydantic import Field
from .contracts import Strict
from .receipts import ReceiptService, RPC, WalletInput, PreviewInput, IssueInput, VerifyInput, verify_package
from .voice import ElevenLabs
from .errors import AppError
from .observability import stage
import uuid
from .github import ComposioGitHub, GitHubService, PRInput, SummaryInput, PublishInput


class SpeechInput(Strict):
    text: str = Field(min_length=1, max_length=3000)


def mount_optional(app, service, auth, config):
    receipts, voice = ReceiptService(service, config), ElevenLabs(config)
    app.state.receipts = receipts
    github_adapter = ComposioGitHub(config)
    github = GitHubService(service, github_adapter)
    app.state.github = github

    def receipts_enabled():
        if not config.solana_enabled:
            raise AppError('receipts_disabled', 'Receipts are disabled for the core demo. Learning checkpoints and history remain available.', 503)

    @app.post('/v1/github/connect')
    def github_connect(owner=Depends(auth)):
        with service.serial(owner):
            return github_adapter.link(owner)

    @app.get('/v1/github/connection')
    def github_connection(owner=Depends(auth)):
        return {'connected': True, 'connection_id': github_adapter.connection(owner)}

    @app.delete('/v1/github/connection')
    def github_unlink(owner=Depends(auth)):
        with service.serial(owner):
            return github_adapter.unlink(owner)

    @app.post('/v1/github/import')
    def github_import(data: PRInput, owner=Depends(auth)):
        with stage('pr_import', str(uuid.uuid4())):
            return github.import_pr(owner, data)

    @app.post('/v1/publications/preview')
    def publication_preview(data: SummaryInput, owner=Depends(auth)):
        return github.preview(owner, data)

    @app.post('/v1/publications')
    def publication(data: PublishInput, owner=Depends(auth)):
        with stage('pr_publication', str(uuid.uuid4())):
            return github.publish(owner, data)

    @app.get('/v1/publications/{id}')
    def publication_status(id: str, owner=Depends(auth)):
        return github.get(owner, id)

    @app.post('/v1/wallet-challenges', dependencies=[Depends(receipts_enabled)])
    def wallet(data: WalletInput, owner=Depends(auth)):
        return receipts.challenge(owner, data)

    @app.post('/v1/receipts/preview', dependencies=[Depends(receipts_enabled)])
    def preview(data: PreviewInput, owner=Depends(auth)):
        return receipts.preview(owner, data)

    @app.post('/v1/receipts', dependencies=[Depends(receipts_enabled)])
    def issue(data: IssueInput, owner=Depends(auth)):
        with stage('receipt_issuance', str(uuid.uuid4())):
            return receipts.issue(owner, data)

    @app.get('/v1/receipts/{id}', dependencies=[Depends(receipts_enabled)])
    def receipt(id: str, owner=Depends(auth)):
        return receipts.get(owner, id)

    @app.post('/v1/receipts/{id}/reconcile', dependencies=[Depends(receipts_enabled)])
    def reconcile(id: str, owner=Depends(auth)):
        with service.serial(owner):
            return receipts.reconcile(owner, id)

    @app.get('/v1/receipts/{id}/export', dependencies=[Depends(receipts_enabled)])
    def export(id: str, owner=Depends(auth)):
        return receipts.get(owner, id, export=True)

    @app.post('/v1/verify', dependencies=[Depends(receipts_enabled)])
    def verify(data: VerifyInput):
        if len(str(data.manifest)) > 250_000:
            raise AppError('too_large', 'Evidence package exceeds the verifier limit.', 413)
        trusted = [x.strip() for x in config.solana_trusted_issuers.split(',') if x.strip()]
        # Bound anonymous RPC work globally; deploy behind per-client proxy limits too.
        with service.serial('__public_verifier__'):
            return verify_package(data.manifest, data.signature, RPC(config.solana_rpc_url), trusted)

    @app.post('/v1/checkpoints/{id}/speech')
    def speech(id: str, data: SpeechInput, owner=Depends(auth)):
        with service.serial(owner):
            cp = service.checkpoint(owner, id)
            allowed = [cp.get('current_question'), (cp.get('question') or {}).get('question')]
            allowed += [a['evaluation']['feedback'] for a in cp['attempts'] if a['evaluation']]
            if data.text not in allowed:
                raise AppError('speech_scope', 'Only this checkpoint question or feedback can be spoken.', 403)
            with stage('speech_playback', str(uuid.uuid4())):
                return Response(voice.speech(data.text), media_type='audio/mpeg')

    @app.post('/v1/audio/transcriptions')
    def transcribe(checkpoint_id: str = Form(...), audio: UploadFile = File(...), owner=Depends(auth)):
        try:
            voice.ready()
            service.checkpoint(owner, checkpoint_id)
            if (audio.content_type or '').split(';')[0] not in {'audio/webm', 'audio/mp4', 'audio/ogg', 'audio/wav', 'audio/mpeg', 'video/webm'}:
                raise AppError('audio_format', 'Unsupported recording format.', 415)
            content = audio.file.read(10_000_001)
            if not content or len(content) > 10_000_000:
                raise AppError('audio_size', 'Record a shorter answer (maximum 10 MB / 90 seconds).', 413)
            with service.serial(owner), stage('transcription', str(uuid.uuid4())):
                return {'text': voice.transcribe(content, audio.content_type), 'requires_review': True, 'submitted': False}
        finally:
            audio.file.close()  # Includes any spooled temporary file. No audio enters application persistence.
