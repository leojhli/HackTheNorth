import json
import time
from sqlalchemy import select
from backend.db import Checkpoint, Operation
from backend.errors import AppError
from backend.retention import expire_context
from tests.conftest import start, change, answer, GOOD, BEFORE, AFTER


def ask(c, session, key='context-ask-0001'):
    return c.post(f"/v1/sessions/{session['id']}/ask", json={'prompt':'Suggest a test for this function','idempotency_key':key})


def passed(c, session):
    cp = change(c, session).json()['checkpoint']
    return answer(c, cp, GOOD).json()


def test_managed_ask_uses_only_approved_after_code_and_reports_provenance(app_env):
    c, app, db, model, _ = app_env
    _, session = start(c)
    cp = passed(c, session)
    result = ask(c, session)
    assert result.status_code == 200
    context = model.last_ask_context
    assert context['source'] == 'approved_saved_after_excerpts'
    assert context['files'][0]['lines'] == cp['snapshot']['files'][0]['lines']
    assert 'edits' not in context['files'][0] and 'before' not in context['files'][0]
    assert GOOD not in json.dumps(context) and 'rubric' not in json.dumps(context)
    meta = result.json()['context']
    assert meta['checkpoint_id'] == cp['id'] and meta['snapshot_hash'] == cp['snapshot_hash']
    assert meta['files'] == ['src/data/findUser.ts'] and meta['reason'] == 'approved_snapshot'
    assert not result.json()['files_modified']
    assert ask(c, session).json() == result.json() and model.ask_calls == 1
    with db.transaction() as tx:
        op = tx.scalar(select(Operation).where(Operation.kind == 'ask'))
        assert 'db.query' not in json.dumps(op.payload)
    app.dependency_overrides[app.state.auth] = lambda: 'someone-else'
    assert ask(c, session, 'cross-owner-ask').status_code == 404
    assert model.ask_calls == 1


def test_scope_revocation_and_no_capture_do_not_reuse_other_code(app_env):
    c, _, _, model, _ = app_env
    project, session = start(c)
    assert ask(c, session).json()['context']['reason'] == 'no_capture'
    assert model.last_ask_context['files'] == []
    passed(c, session)
    result = c.post(f"/v1/projects/{project['id']}/scope", json={'name':project['name'],'scope':['src/elsewhere'],'exclusions':[], 'expected_scope_hash':project['scope_hash']})
    assert result.status_code == 200
    assert ask(c, session, 'after-scope-change').json()['context']['reason'] == 'no_eligible_source'
    assert model.last_ask_context['files'] == []
    c.post(f"/v1/sessions/{session['id']}/end")
    p = c.post('/v1/projects',json={'name':'Other project','scope':['src']}).json()
    other = c.post('/v1/sessions',json={'project_id':p['id']}).json()
    assert ask(c, other, 'other-project-request').json()['context']['reason'] == 'no_capture'
    assert model.last_ask_context['files'] == []


def test_interrupted_ask_keeps_original_snapshot_and_checks_changed_scope(app_env):
    c, _, _, model, _ = app_env
    project, session = start(c)
    first = passed(c, session)
    original = model.ask
    def fail(prompt, context):
        raise AppError('local_model_timeout','Synthetic outage',503,True)
    model.ask = fail
    assert ask(c, session).status_code == 503
    cp = c.post(f"/v1/sessions/{session['id']}/changes",json={'files':[{'path':'src/new.ts','before':BEFORE,'after':AFTER}],'idempotency_key':'second-context-change'}).json()['checkpoint']
    answer(c, cp, GOOD)
    model.ask = original
    retried = ask(c, session).json()
    assert retried['context']['checkpoint_id'] == first['id']
    assert ask(c, session, 'fresh-context-request').json()['context']['checkpoint_id'] == cp['id']
    model.ask = fail
    assert ask(c, session, 'scope-interrupted').status_code == 503
    c.post(f"/v1/projects/{project['id']}/scope", json={'name':project['name'],'scope':['src/new.ts'],'exclusions':[], 'expected_scope_hash':project['scope_hash']})
    model.ask = original
    assert ask(c, session, 'scope-interrupted').json()['code'] == 'ask_context_changed'


def test_expiry_removes_derived_response_and_never_falls_back_to_older_code(app_env):
    c, _, db, model, _ = app_env
    _, session = start(c)
    cp = passed(c, session)
    assert ask(c, session).status_code == 200
    with db.transaction() as tx:
        tx.get(Checkpoint,cp['id']).created = time.time()-31*86400
    expire_context(db)
    cached = ask(c, session).json()
    assert 'expired' in cached['text'] and cached['context']['files'] == []
    assert ask(c, session, 'fresh-after-expiry').json()['context']['reason'] == 'source_expired'
    assert model.last_ask_context['files'] == []


def test_expiry_during_inference_discards_response_without_state_changes(app_env):
    c, _, db, model, _ = app_env
    _, session = start(c)
    cp = passed(c, session)
    def expire(prompt, context):
        with db.transaction() as tx:
            tx.get(Checkpoint,cp['id']).created = time.time()-31*86400
        expire_context(db)
        return 'Source-derived response must not be saved.'
    model.ask = expire
    result = ask(c, session)
    assert result.status_code == 409 and result.json()['code'] == 'ask_context_changed'
    assert c.get(f"/v1/checkpoints/{cp['id']}").json()['status'] == 'passed'
    with db.transaction() as tx:
        assert tx.scalar(select(Operation).where(Operation.kind == 'ask')).result is None


def test_context_agent_stays_behind_gate_and_cached_result_keeps_binding(app_env, monkeypatch):
    from backend.assessment import LocalAssessor
    c, app, db, model, conf = app_env
    _, session = start(c)
    response = c.post(f"/v1/sessions/{session['id']}/changes", json={'files':[
        {'path':'src/main.ts','before':BEFORE,'after':AFTER},
        {'path':'src/noise.ts','before':'export const n=1;','after':'export const n=2;'}],
        'idempotency_key':'agent-multifile-change'})
    cp = response.json()['checkpoint']
    local = LocalAssessor(conf)
    calls=[]
    def generate(messages, schema=None, **kwargs):
        calls.append(messages)
        return schema(tool='inspect_module:src/main.ts',missing_context='') if schema else 'Grounded suggestion.'
    monkeypatch.setattr(local,'generate',generate)
    model.ask=local.ask
    assert ask(c,session).status_code==409 and not calls
    answer(c,cp,GOOD)
    result=ask(c,session)
    assert result.status_code==200 and 'src/main.ts' in result.json()['text']
    assert len(calls)==2 and 'export const n=2' not in json.dumps(calls)
    assert ask(c,session).json()==result.json() and len(calls)==2
    assert c.get(f"/v1/checkpoints/{cp['id']}").json()['status']=='passed'
