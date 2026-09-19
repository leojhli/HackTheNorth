"""Opt-in live local-model smoke check using synthetic source and a temporary DB.

Run: python -m scripts.verify_local_ai
No paid APIs, fixture evaluator, user history, or external publications are used.
"""
import json
import tempfile
import time
from pathlib import Path
from fastapi.testclient import TestClient
from backend.config import Settings
from backend.db import Database
from backend.main import create_app
from scripts.prepare_demo import DEMO_CASE

CASES = [
    {
        'name': 'SQL bound parameter',
        'before': 'export function findUser(db, email) {\n  return db.query(`SELECT * FROM users WHERE email = "${email}"`);\n}',
        'after': 'export function findUser(db, email) {\n  return db.query("SELECT * FROM users WHERE email = $1", [email]);\n}',
        'weak': 'It makes the database safer.',
        'good': 'The SQL structure is fixed with the $1 placeholder. The database driver binds email separately as a data value, so quotes or SQL keywords in email cannot alter query syntax. This prevents SQL injection at this parameter, but business validation and authorization are still needed. This assumes db.query supports PostgreSQL-style bound parameters.'
    },
    {
        'name': 'Null input guard',
        'before': 'export function displayName(user) {\n  return user.name.trim();\n}',
        'after': 'export function displayName(user) {\n  if (user == null) return "Guest";\n  return user.name.trim();\n}',
        'weak': None,
        'good': 'The guard returns Guest before reading user.name when user is null or undefined: loose equality to null matches both. This prevents dereferencing a missing user and keeps trimming for existing users. It does not validate user.name: a missing, null or non-string name can still throw. Guest is a display fallback, not proof that a user is authenticated.'
    },
    {
        'name': 'Nonmutating sort',
        'before': 'export function sortedScores(scores) {\n  return scores.sort((a, b) => a - b);\n}',
        'after': 'export function sortedScores(scores) {\n  return [...scores].sort((a, b) => a - b);\n}',
        'weak': 'It sorts better.',
        'good': 'Spread creates a new shallow array before sort mutates it. The caller\'s scores array therefore keeps its original order, while the returned copy is sorted in ascending numeric order by a minus b. It allocates an extra array, unlike sorting in place, and does not deeply clone nested objects. The comparator assumes numeric scores; NaN and nonnumeric values still need validation.'
    },
]


def main(demo=False):
    selected = CASES if not demo else [DEMO_CASE]
    report = {'provider': 'local Ollama, actual inference', 'cases': [], 'requests': []}
    with tempfile.TemporaryDirectory(prefix='beprogram-local-live-') as directory:
        config = Settings(database_url='sqlite:///' + str(Path(directory) / 'smoke.db'),
                          environment='test', auth_mode='local', local_dev_token='isolated-live-check-not-a-user-token-123')
        report['model'] = config.ollama_model
        database = Database(config.database_url)
        app = create_app(config, database)
        client = TestClient(app, headers={'Authorization': 'Bearer ' + config.local_dev_token})
        def request(method, path, body=None):
            began = time.monotonic()
            response = client.request(method, path, json=body)
            entry = {'method': method, 'path': path, 'status': response.status_code, 'seconds': round(time.monotonic() - began, 2)}
            if response.status_code != 200:
                entry['error'] = response.json().get('code', 'http_error')
            report['requests'].append(entry)
            print(json.dumps(entry), flush=True)
            assert response.status_code == 200, response.text
            return response.json()
        try:
            assert request('GET', '/v1/config')['ai']['available'], 'Install/start the local model first'
            for index, case in enumerate(selected):
                project = request('POST', '/v1/projects', {'name': case['name'], 'scope': ['src']})
                session = request('POST', '/v1/sessions', {'project_id': project['id']})
                capture = {'files': [{'path': case.get('path', 'src/example.ts'), 'before': case['before'], 'after': case['after']}],
                           'provenance': 'user_reported_manual', 'idempotency_key': f'live-change-{index}'}
                cp = request('POST', f"/v1/sessions/{session['id']}/changes", capture)['checkpoint']
                assert cp['status'] == 'pending', cp
                report_case = {'name': case['name'], 'question': cp['question'], 'attempts': []}
                report['cases'].append(report_case)
                if case['weak']:
                    cp = request('POST', f"/v1/checkpoints/{cp['id']}/answers", {'answer': case['weak'],
                        'version': cp['version'], 'snapshot_hash': cp['snapshot_hash'], 'idempotency_key': f'live-weak-{index}'})
                    report_case['attempts'] = cp['attempts']
                    assert cp['status'] == 'needs_followup', cp
                    assert not request('GET', f"/v1/sessions/{session['id']}/gate")['available']
                cp = request('POST', f"/v1/checkpoints/{cp['id']}/answers", {'answer': case['good'],
                    'version': cp['version'], 'snapshot_hash': cp['snapshot_hash'], 'idempotency_key': f'live-good-{index}'})
                report_case['attempts'] = cp['attempts']
                assert cp['status'] == 'passed', cp
                assert request('GET', f"/v1/sessions/{session['id']}/gate")['available']
                result = request('POST', f"/v1/sessions/{session['id']}/ask", {'prompt': 'Suggest one short edge-case test for this code:\n' + case['after'], 'idempotency_key': f'live-ask-{index}'})
                assert result['text'].strip()
                report_case['managed_reply'] = result['text']
                request('POST', f"/v1/sessions/{session['id']}/end")
            assert len(request('GET', '/v1/history')) == len(selected)
            # Recreate service/client over the same DB: state must survive restart.
            with TestClient(create_app(config, database), headers={'Authorization': 'Bearer ' + config.local_dev_token}) as restored:
                assert all(cp['status'] == 'passed' for cp in restored.get('/v1/history').json())
            report['passed'] = True
        finally:
            database.engine.dispose()
            Path('docs/beginner-demo-result.json' if demo else 'docs/local-model-smoke.json').write_text(json.dumps(report, indent=2), encoding='utf-8')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--demo', action='store_true', help='Rehearse the beginner event-capacity demo through the actual API/model.')
    main(parser.parse_args().demo)
