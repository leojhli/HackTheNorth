import time
import uuid
from pathlib import Path
from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from sqlalchemy import text
from .config import settings
from .db import Database, Attempt
from .auth import Auth
from .assessment import LocalAssessor
from .service import CheckpointService, owned, record
from .contracts import ProjectInput, ScopeInput, SessionInput, ChangeInput, AnswerInput, AskInput, CheckpointBinding
from .errors import AppError
from . import observability


def create_app(config=None, database=None, assessor=None):
    config = config or settings()
    database = database or Database(config.database_url)
    if config.environment != 'production':
        database.migrate()
    service = CheckpointService(database, assessor or LocalAssessor(config), config)
    auth = Auth(config)
    observability.configure(config)
    app = FastAPI(title='BeProgram', version='0.1.0')
    app.state.service, app.state.auth, app.state.config = service, auth, config
    app.add_middleware(CORSMiddleware, allow_origins=config.allowed_origins.split(','), allow_credentials=False,
        allow_methods=['GET', 'POST', 'DELETE'], allow_headers=['Authorization', 'Content-Type'])

    @app.exception_handler(AppError)
    async def error(request, exc):
        return JSONResponse({'code': exc.code, 'message': exc.message, 'retryable': exc.retryable}, status_code=exc.status)

    @app.exception_handler(RequestValidationError)
    async def validation(request, exc):
        # Pydantic's original input may contain code, credentials or private answers.
        return JSONResponse({'code': 'invalid_input', 'message': 'Check the required fields, formats and size limits.', 'retryable': False}, status_code=422)

    @app.middleware('http')
    async def boundaries(request: Request, call_next):
        try:
            length = int(request.headers.get('content-length', 0) or 0)
        except ValueError:
            length = 12_000_001
        if length > 12_000_000:
            return JSONResponse({'code': 'too_large', 'message': 'Request exceeds the 12 MB limit.', 'retryable': False}, status_code=413)
        if request.method in {'POST', 'PUT', 'PATCH'}:
            chunks, received = [], 0
            async for chunk in request.stream():
                received += len(chunk)
                if received > 12_000_000:
                    return JSONResponse({'code': 'too_large', 'message': 'Request exceeds the 12 MB limit.', 'retryable': False}, status_code=413)
                chunks.append(chunk)
            request._body = b''.join(chunks)
        origin = request.headers.get('origin')
        if request.method in {'POST', 'DELETE'} and origin and origin not in config.allowed_origins.split(',') + [config.app_origin]:
            return JSONResponse({'code': 'origin_rejected', 'message': 'This origin is not permitted.', 'retryable': False}, status_code=403)
        try:
            response = await call_next(request)
        except Exception:
            response = JSONResponse({'code': 'internal_error', 'message': 'The operation failed. Refresh to reconcile saved state.', 'retryable': True}, status_code=500)
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Referrer-Policy'] = 'no-referrer'
        response.headers['Cache-Control'] = 'no-store'
        return response

    @app.get('/health')
    def health():
        with database.transaction() as db:
            db.execute(text('SELECT 1'))
        return {'status': 'ok'}

    @app.get('/v1/config')
    def public_config():
        ai = service.assessor.status() if hasattr(service.assessor, 'status') else {'available': True, 'provider': 'test-only-fixture', 'model': 'test-only-fixture', 'message': 'Injected test fixture; not live inference.'}
        return {'auth_mode': config.auth_mode, 'supabase_url': config.supabase_url, 'supabase_publishable_key': config.supabase_publishable_key,
                'ai': ai, 'cost_mode': 'local_only',
                'diagnostics': {'sentry_enabled': config.sentry_enabled, 'products': ['Logs', 'Tracing'] if config.sentry_enabled else []},
                'capabilities': {'assessment': ai['available'], 'managed_ai': ai['available'],
                    'voice': False,
                    'receipts': bool(config.solana_enabled and config.solana_issuer_key),
                    'github': False},
                'integration': 'beprogram_managed', 'provenance_note': 'A diff does not establish AI authorship.'}

    @app.get('/v1/projects')
    def projects(owner=Depends(auth)):
        return service.projects(owner)

    @app.post('/v1/projects')
    def create_project(data: ProjectInput, owner=Depends(auth)):
        return service.create_project(owner, data)

    @app.delete('/v1/projects/{id}')
    def remove_project(id: str, owner=Depends(auth)):
        return service.delete_project(owner, id)

    @app.post('/v1/projects/{id}/scope')
    def update_scope(id: str, data: ScopeInput, owner=Depends(auth)):
        return service.update_scope(owner, id, data)

    @app.get('/v1/sessions')
    def sessions(owner=Depends(auth)):
        return service.sessions(owner)

    @app.post('/v1/sessions')
    def start(data: SessionInput, owner=Depends(auth)):
        return service.start(owner, data.project_id)

    @app.post('/v1/sessions/{id}/end')
    def end(id: str, owner=Depends(auth)):
        return service.end(owner, id)

    @app.post('/v1/sessions/{id}/changes')
    def changes(id: str, data: ChangeInput, owner=Depends(auth)):
        with observability.stage('change_filter_and_question', str(uuid.uuid4())):
            return service.change(owner, id, data)

    @app.get('/v1/checkpoints/{id}')
    def checkpoint(id: str, owner=Depends(auth)):
        return service.checkpoint(owner, id)

    @app.post('/v1/checkpoints/{id}/retry')
    def retry(id: str, owner=Depends(auth)):
        return service.retry_question(owner, id)

    @app.post('/v1/checkpoints/{id}/explanation')
    def explanation(id: str, owner=Depends(auth)):
        with observability.stage('checkpoint_explanation', str(uuid.uuid4())):
            return service.explain(owner, id)

    @app.post('/v1/checkpoints/{id}/answers')
    def answer(id: str, data: AnswerInput, owner=Depends(auth)):
        with observability.stage('answer_evaluation_and_persistence', str(uuid.uuid4())):
            return service.answer(owner, id, data)

    @app.post('/v1/checkpoints/{id}/practice')
    def practice(id: str, data: CheckpointBinding, owner=Depends(auth)):
        with observability.stage('practice_question', str(uuid.uuid4())):
            return service.start_practice(owner, id, data)

    @app.get('/v1/attempts/{id}')
    def attempt(id: str, owner=Depends(auth)):
        with database.transaction() as db:
            return record(owned(db, Attempt, id, owner))

    @app.get('/v1/sessions/{id}/gate')
    def gate(id: str, owner=Depends(auth)):
        with observability.stage('gate_reconciliation', str(uuid.uuid4())):
            return service.gate(owner, id)

    @app.get('/v1/history')
    def history(owner=Depends(auth)):
        return service.history(owner)

    @app.get('/v1/sessions/{id}/history')
    def session_history(id: str, owner=Depends(auth)):
        return service.history(owner, id)

    @app.post('/v1/sessions/{id}/ask')
    def ask(id: str, data: AskInput, owner=Depends(auth)):
        with observability.stage('managed_ask', str(uuid.uuid4())):
            return service.ask(owner, id, data)

    from .optional_routes import mount_optional
    mount_optional(app, service, auth, config)
    dist = Path('apps/dashboard/dist')
    if dist.exists():
        app.mount('/assets', StaticFiles(directory=dist / 'assets'), name='assets')
        @app.get('/{path:path}', include_in_schema=False)
        def frontend(path: str):
            if path.startswith(('v1/', 'health', 'docs')):
                raise AppError('not_found', 'Endpoint not found.', 404)
            return FileResponse(dist / 'index.html')
    return app


app = create_app()
