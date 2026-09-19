"""Retention may run while local inference holds a detached source snapshot."""
import time
import pytest
from sqlalchemy import select
from backend.db import Checkpoint
from backend.retention import expire_context
from tests.conftest import start, change, answer, GOOD, PRACTICE_GOOD


def expire_all(db):
    with db.transaction() as tx:
        for cp in tx.scalars(select(Checkpoint)):
            cp.created = time.time() - 31 * 86400
    expire_context(db)


@pytest.mark.parametrize('assisted', [False, True])
def test_expiry_during_answer_preserves_attempt_without_granting_pass(app_env, assisted):
    c, _, db, model, _ = app_env
    _, session = start(c)
    cp = change(c, session).json()['checkpoint']
    if assisted:
        c.post(f"/v1/checkpoints/{cp['id']}/explanation")
        cp = c.post(f"/v1/checkpoints/{cp['id']}/practice", json={
            'version': cp['version'], 'snapshot_hash': cp['snapshot_hash']}).json()
    original = model.evaluate

    def during_inference(checkpoint, attempts, text):
        result = original(checkpoint, attempts, text)
        assert result.decision == 'pass'
        expire_all(db)
        return result

    model.evaluate = during_inference
    text = PRACTICE_GOOD if assisted else GOOD
    response = answer(c, cp, text)
    assert response.status_code == 409 and response.json()['code'] == 'context_expired'
    saved = c.get(f"/v1/checkpoints/{cp['id']}").json()
    assert saved['status'] == 'unavailable' and saved['passed_at'] is None
    assert saved['version'] == cp['version'] and saved['last_error'] == 'context_expired'
    assert len(saved['attempts']) == 1
    attempt = saved['attempts'][0]
    assert attempt['answer'] == text and attempt['state'] == 'failed'
    assert attempt['error'] == 'context_expired' and attempt['evaluation'] is None
    assert not c.get(f"/v1/sessions/{session['id']}/gate").json()['available']
    assert answer(c, cp, text).json()['code'] == 'context_expired'
    assert model.answer_calls == 1


@pytest.mark.parametrize('retry', [False, True])
def test_expiry_during_question_does_not_restore_source_derived_question(app_env, retry):
    c, _, db, model, _ = app_env
    _, session = start(c)
    original = model.question
    if retry:
        model.fail = True
        assert change(c, session).status_code == 503
        cp = c.get('/v1/history').json()[0]
        model.fail = False

    def during_inference(snapshot, recent):
        result = original(snapshot, recent)
        expire_all(db)
        return result

    model.question = during_inference
    response = c.post(f"/v1/checkpoints/{cp['id']}/retry") if retry else change(c, session)
    assert response.status_code == 409 and response.json()['code'] == 'context_expired'
    saved = c.get('/v1/history').json()[0]
    assert saved['status'] == 'unavailable' and saved['question'] is None
    assert saved['last_error'] == 'context_expired'
    assert not c.get(f"/v1/sessions/{session['id']}/gate").json()['available']
