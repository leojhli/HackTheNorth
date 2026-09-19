import pytest
from fastapi.testclient import TestClient
from backend.config import Settings
from backend.db import Database
from backend.main import create_app
from backend.contracts import Question, Evaluation
from backend.errors import AppError

BEFORE = 'export async function findUser(db, email) {\n  return db.query(`SELECT * FROM users WHERE email = "${email}"`);\n}'
AFTER = 'export async function findUser(db, email) {\n  return db.query("SELECT * FROM users WHERE email = $1", [email]);\n}'
PRACTICE_GOOD = "O'Reilly stays a single bound email value. The driver passes it as data for $1, so the apostrophe cannot change the SQL query structure. This does not validate whether the email is allowed."


class FixtureAssessor:
    """Deterministic test double. It is never loaded by application configuration."""
    fail = False
    question_calls = 0
    answer_calls = 0
    ask_calls = 0

    def question(self, snapshot, recent):
        self.question_calls += 1
        if self.fail:
            raise AppError('provider_timeout', 'Test provider timed out.', 503, True)
        f = snapshot['files'][0]
        line = next(l for l in f['lines'] if 'db.query' in l['text'])
        return Question(decision='assess', concept='SQL parameterization',
            question='How does separating the query from email change the treatment of malicious input?',
            reason='The change separates SQL structure from a bound value.', rubric=['intent', 'mechanism', 'edge case'],
            evidence=[{'path': f['path'], 'start_line': line['number'], 'end_line': line['number'], 'quote': line['text']}], important_distinct_use=False)

    def evaluate(self, checkpoint, attempts, answer):
        self.answer_calls += 1
        if self.fail:
            raise AppError('provider_timeout', 'Test provider timed out.', 503, True)
        passed = answer == 'The query structure is fixed. The driver binds email as data, so quotes in email cannot change SQL syntax. Input validation is still needed for business rules.'
        if getattr(checkpoint, 'practice', False):
            passed = answer == PRACTICE_GOOD
        return Evaluation(decision='pass' if passed else 'follow_up', intent_correct=True,
            mechanism_correct=passed, reasoning_correct=passed, central_contradiction=False,
            feedback='You explained structure, binding and the limit.' if passed else 'Explain how the value reaches the database.',
            evidence=['Bound parameter'], gaps=[] if passed else ['mechanism'], next_question=None if passed else 'What does the driver do with email and the $1 placeholder?')

    def ask(self, prompt, context=None):
        self.ask_calls += 1
        self.last_ask_context = context
        return 'Test-only coding assistant response.'

    def explain(self, checkpoint):
        if self.fail:
            raise AppError('provider_timeout', 'Test provider timed out.', 503, True)
        return 'Test-only explanation: the driver binds email as data instead of SQL syntax.'

    def practice(self, checkpoint, explanation):
        question = self.question(checkpoint.snapshot, [])
        return question.model_copy(update={'question': "If email contains O'Reilly, how is its apostrophe handled by this query and why?"})


@pytest.fixture
def app_env(tmp_path):
    config = Settings(_env_file=None, environment='test', database_url='sqlite:///' + str(tmp_path/'test.db'),
        auth_mode='local', local_dev_token='test-local-token-not-for-production-123')
    db = Database(config.database_url)
    model = FixtureAssessor()
    app = create_app(config, db, model)
    client = TestClient(app, headers={'Authorization': 'Bearer ' + config.local_dev_token})
    yield client, app, db, model, config
    db.engine.dispose()


def start(client):
    project = client.post('/v1/projects', json={'name': 'campus-events', 'scope': ['src']}).json()
    session = client.post('/v1/sessions', json={'project_id': project['id']}).json()
    return project, session


def change(client, session, key='change-0001'):
    return client.post(f"/v1/sessions/{session['id']}/changes", json={'files': [{'path': 'src/data/findUser.ts', 'before': BEFORE, 'after': AFTER}],
        'provenance': 'user_reported_manual', 'idempotency_key': key})


def answer(client, cp, text, key='answer-0001'):
    return client.post(f"/v1/checkpoints/{cp['id']}/answers", json={'answer': text, 'version': cp['version'],
        'snapshot_hash': cp['snapshot_hash'], 'idempotency_key': key})


GOOD = 'The query structure is fixed. The driver binds email as data, so quotes in email cannot change SQL syntax. Input validation is still needed for business rules.'
