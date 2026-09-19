import json
import logging
import uuid
import httpx
import pytest
from backend import observability
from backend.config import Settings
from backend.errors import AppError
from scripts.doctor import inspect


def test_local_lifecycle_logs_are_redacted_bounded_and_correlated(tmp_path, monkeypatch):
    logger = logging.Logger('test-local-lifecycle')
    monkeypatch.setattr(observability, 'local_logger', logger)
    destination = tmp_path / 'logs' / 'lifecycle.jsonl'
    config = Settings(_env_file=None, local_log_path=str(destination))
    observability.configure(config)
    correlation = str(uuid.uuid4())
    with pytest.raises(AppError):
        with observability.stage('answer_evaluation_and_persistence', correlation):
            raise AppError('ungrounded_local_pass', 'PRIVATE_ANSWER_AND_TOKEN', 503)
    observability.local_event('PRIVATE_PATH', 'PRIVATE_SOURCE', 'error', 10, 'PRIVATE_TOKEN')
    raw = destination.read_text(encoding='utf-8')
    assert 'PRIVATE_' not in raw
    entries = [json.loads(line) for line in raw.splitlines()]
    assert entries[0]['correlation_id'] == correlation
    assert entries[0]['category'] == 'ungrounded_local_pass' and entries[0]['status'] == 'error'
    with observability.stage('managed_ask', correlation):
        with observability.stage('local_inference'):
            pass
    nested = [json.loads(line) for line in destination.read_text(encoding='utf-8').splitlines()][-2:]
    assert {e['correlation_id'] for e in nested} == {correlation}
    assert [e['operation'] for e in nested] == ['local_inference', 'managed_ask']
    file_handler = next(h for h in logger.handlers if hasattr(h, 'maxBytes'))
    assert file_handler.maxBytes == 1_000_000 and file_handler.backupCount == 3
    monkeypatch.setattr(file_handler, 'emit', lambda *a: (_ for _ in ()).throw(OSError('disk full')))
    with observability.stage('managed_ask', str(uuid.uuid4())):
        pass  # Telemetry failure cannot change a successful request.
    for handler in logger.handlers:
        handler.close()


def test_doctor_does_not_expose_credentials_or_private_response(monkeypatch):
    monkeypatch.setattr('scripts.doctor.LocalAssessor.status', lambda self: {'available': True, 'message': 'Installed'})
    config = Settings(_env_file=None, auth_mode='local', local_dev_token='PRIVATE_SECRET_TOKEN_12345678901234567890')
    seen = []
    def handler(request):
        seen.append(request)
        if request.url.path == '/health':
            return httpx.Response(200, json={'status': 'ok'})
        if request.url.path == '/v1/config':
            return httpx.Response(200, json={'integration': 'beprogram_managed', 'cost_mode': 'local_only', 'ai': {'model': config.ollama_model}})
        return httpx.Response(200, json=[{'name': 'PRIVATE_PROJECT', 'answer': 'PRIVATE_ANSWER'}])
    with httpx.Client(base_url='http://127.0.0.1:8000', transport=httpx.MockTransport(handler)) as client:
        report = inspect(config, client)
    assert 'PRIVATE_' not in json.dumps(report)
    assert seen[-1].headers['authorization'] == 'Bearer ' + config.local_dev_token
    assert next(c for c in report['checks'] if c['check'] == 'local_token')['ok']


def test_doctor_reports_wrong_token_without_printing_response(monkeypatch):
    monkeypatch.setattr('scripts.doctor.LocalAssessor.status', lambda self: {'available': False, 'message': 'Start local AI.'})
    config = Settings(_env_file=None, auth_mode='local', local_dev_token='PRIVATE_SECRET_TOKEN_12345678901234567890')
    def handler(request):
        if request.url.path == '/health': return httpx.Response(200, json={'status': 'ok'})
        if request.url.path == '/v1/config': return httpx.Response(200, json={})
        return httpx.Response(401, json={'message': 'PRIVATE_ERROR'})
    with httpx.Client(base_url='http://127.0.0.1:8000', transport=httpx.MockTransport(handler)) as client:
        report = inspect(config, client)
    assert not report['ready']
    assert not next(c for c in report['checks'] if c['check'] == 'local_token')['ok']
    assert 'PRIVATE_' not in json.dumps(report)
