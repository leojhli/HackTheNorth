"""Regression coverage for explanation/practice state; test-only assessor, not model validation."""
import time
from types import SimpleNamespace
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from backend.assessment import LocalAssessor, PracticeEvaluation
from backend.db import Checkpoint, Operation
from backend.main import create_app
from backend.retention import expire_context
from tests.conftest import start, change, answer, GOOD, PRACTICE_GOOD


def setup(c):
    p, s = start(c)
    cp = change(c, s).json()['checkpoint']
    cp = answer(c, cp, 'It makes it safer.').json()
    return p, s, cp


def practice(c, cp):
    return c.post(f"/v1/checkpoints/{cp['id']}/practice",json={'version':cp['version'],'snapshot_hash':cp['snapshot_hash']})


def test_help_is_durable_without_passing_and_expires_with_source(app_env):
    c, _, db, model, _ = app_env
    _, s, cp = setup(c)
    route=f"/v1/checkpoints/{cp['id']}/explanation"
    helped=c.post(route).json()
    assert helped['learning_explanation'] and helped['explanation_viewed']
    assert helped['version']==cp['version'] and helped['status']==cp['status'] and not helped['passed_at']
    assert helped['attempts']==cp['attempts']
    model.fail=True
    assert c.post(route).json()['learning_explanation']==helped['learning_explanation']
    assert not c.get(f"/v1/sessions/{s['id']}/gate").json()['available']
    assert answer(c,cp,GOOD,'old-after-help').json()['code']=='practice_required'
    with db.transaction() as tx:tx.get(Checkpoint,cp['id']).created=time.time()-31*86400
    expire_context(db)
    saved=c.get(f"/v1/checkpoints/{cp['id']}").json()
    assert saved['explanation_viewed'] and saved['learning_explanation'] is None


def test_explanation_outage_retry_keeps_answers(app_env):
    c, _, _, model, _=app_env
    _, _, cp=setup(c)
    model.fail=True
    assert c.post(f"/v1/checkpoints/{cp['id']}/explanation").status_code==503
    saved=c.get(f"/v1/checkpoints/{cp['id']}").json()
    assert saved['attempts']==cp['attempts'] and not saved['explanation_viewed']
    model.fail=False
    assert c.post(f"/v1/checkpoints/{cp['id']}/explanation").status_code==200


def test_fresh_practice_survives_restart_and_cannot_use_old_answers(app_env):
    c, _, db, model, config=app_env
    _, s, cp=setup(c)
    c.post(f"/v1/checkpoints/{cp['id']}/explanation")
    fresh=practice(c,cp).json()
    assert fresh['question']==cp['question'] and fresh['attempts']==cp['attempts']
    assert fresh['version']==cp['version']+1 and fresh['practice_question']
    assert answer(c,cp,GOOD,'stale-original').json()['code']=='stale_version'
    assert practice(c,cp).json()['version']==fresh['version']
    prior=[];evaluate=model.evaluate
    def spy(checkpoint,attempts,text):
        assert checkpoint.practice and checkpoint.question==fresh['practice_question']
        prior.append(attempts)
        return evaluate(checkpoint,attempts,text)
    model.evaluate=spy
    with TestClient(create_app(config,db,model),headers=dict(c.headers)) as restarted:
        saved=restarted.get(f"/v1/checkpoints/{cp['id']}").json()
        assert saved['current_question']==fresh['practice_question']['question']
        weak=answer(restarted,fresh,GOOD,'generic-old-answer').json()
        assert weak['status']=='needs_followup' and prior[0]==[]
        final=answer(restarted,weak,PRACTICE_GOOD,'correct-practice').json()
        assert final['status']=='passed_with_help' and final['passed_at']
        assert len(prior[1])==1 and prior[1][0]['version']>=fresh['practice_started_version']
        assert answer(restarted,weak,PRACTICE_GOOD,'correct-practice').json()['status']=='passed_with_help'
        assert restarted.get(f"/v1/sessions/{s['id']}/gate").json()['available']


def test_practice_prerequisite_ownership_expiry_and_staleness(app_env):
    c, app, db, model, _=app_env
    _, _, cp=setup(c)
    assert practice(c,cp).json()['code']=='explanation_required'
    c.post(f"/v1/checkpoints/{cp['id']}/explanation")
    assert practice(c,{**cp,'version':999}).json()['code']=='stale_version'
    assert practice(c,{**cp,'snapshot_hash':'0'*64}).json()['code']=='stale_version'
    app.dependency_overrides[app.state.auth]=lambda:'other-owner'
    assert practice(c,cp).status_code==404
    app.dependency_overrides.clear()
    model.fail=True
    assert practice(c,cp).status_code==503
    assert c.get(f"/v1/checkpoints/{cp['id']}").json()['version']==cp['version']
    with db.transaction() as tx:tx.get(Checkpoint,cp['id']).created=time.time()-31*86400
    expire_context(db)
    assert practice(c,cp).json()['code']=='context_expired'


@pytest.mark.parametrize('kind',['same','skip','ungrounded'])
def test_invalid_practice_cannot_replace_question_or_unlock(app_env,kind):
    c, _, _, model, _=app_env
    _, s, cp=setup(c)
    c.post(f"/v1/checkpoints/{cp['id']}/explanation")
    def invalid(checkpoint,explanation):
        q=model.question(checkpoint.snapshot,[])
        if kind=='skip':return q.model_copy(update={'decision':'skip'})
        if kind=='ungrounded':return q.model_copy(update={'question':'A new scenario?', 'evidence':[q.evidence[0].model_copy(update={'quote':'Invented code'})]})
        return q
    model.practice=invalid
    assert practice(c,cp).status_code>=400
    saved=c.get(f"/v1/checkpoints/{cp['id']}").json()
    assert saved['version']==cp['version'] and saved['question']==cp['question'] and not saved['practice_question']
    assert not c.get(f"/v1/sessions/{s['id']}/gate").json()['available']


@pytest.mark.parametrize('dimension',['intent_correct','mechanism_correct','reasoning_correct','central_contradiction','gaps'])
def test_practice_missing_dimensions_never_pass(app_env,dimension):
    model=LocalAssessor(app_env[4])
    data={'answer_quotes':['My answer'],'intent_correct':True,'mechanism_correct':True,'reasoning_correct':True,'central_contradiction':False,'gaps':[],'feedback':'Recheck this example.','evidence':[]}
    data[dimension]=['Missing reasoning'] if dimension=='gaps' else dimension=='central_contradiction'
    model.generate=lambda *a,**kw:PracticeEvaluation(**data)
    cp=SimpleNamespace(snapshot={},question={'question':'What happens for eight guests and ten spaces?'},practice=True)
    result=model.evaluate(cp,[],'My answer')
    assert result.decision=='follow_up' and result.next_question==cp.question['question']


def test_practice_answer_outage_retry_and_deletion(app_env):
    c, _, db, model, _=app_env
    p,s,cp=setup(c)
    c.post(f"/v1/checkpoints/{cp['id']}/explanation")
    fresh=practice(c,cp).json();model.fail=True
    assert answer(c,fresh,PRACTICE_GOOD,'practice-outage').status_code==503
    saved=c.get(f"/v1/checkpoints/{cp['id']}").json()
    assert saved['attempts'][-1]['answer']==PRACTICE_GOOD and saved['practice_question']==fresh['practice_question']
    assert not c.get(f"/v1/sessions/{s['id']}/gate").json()['available']
    model.fail=False
    assert answer(c,fresh,PRACTICE_GOOD,'practice-outage').json()['status']=='passed_with_help'
    assert c.delete(f"/v1/projects/{p['id']}").status_code==200
    with db.transaction() as tx:assert tx.scalar(select(Operation).where(Operation.project_id==p['id'])) is None
