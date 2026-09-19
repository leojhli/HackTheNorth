import time
from fastapi.testclient import TestClient
from sqlalchemy import select
from backend.main import create_app
from backend.db import Lease, Checkpoint, Attempt, uid
from backend.config import Settings
from backend.context import capture, validate_evidence
from backend.contracts import FileChange, Evaluation
from backend.observability import scrub_event, scrub_log
from tests.conftest import start, change, answer, GOOD, BEFORE, AFTER
import pytest


def test_followup_pass_history_and_managed_gate(app_env):
    c, app, db, model, config = app_env
    p, s = start(c)
    r = change(c, s)
    assert r.status_code == 200, r.text
    cp = r.json()['checkpoint']
    assert c.get(f"/v1/sessions/{s['id']}/gate").json()['available'] is False
    assert c.post(f"/v1/sessions/{s['id']}/ask", json={'prompt': 'Write a helper', 'idempotency_key': 'ask-00001'}).status_code == 409
    cp = answer(c, cp, 'It makes the database safer.').json()
    assert cp['status'] == 'needs_followup'
    assert '$1' in cp['current_question']
    cp = answer(c, cp, GOOD, 'answer-0002').json()
    assert cp['status'] == 'passed'
    assert cp['passed_at']
    assert len(cp['attempts']) == 2
    assert c.get(f"/v1/sessions/{s['id']}/gate").json()['available']
    r = c.post(f"/v1/sessions/{s['id']}/ask", json={'prompt': 'Write a helper', 'idempotency_key': 'ask-00001'})
    assert r.status_code == 200 and r.json()['files_modified'] is False
    assert c.get('/v1/history').json()[0]['status'] == 'passed'
    assert model.ask_calls == 1


def test_first_answer_duplicate_and_stale(app_env):
    c, _, _, model, _ = app_env
    _, s = start(c)
    cp = change(c, s).json()['checkpoint']
    assert change(c, s).json()['duplicate']
    assert model.question_calls == 1
    first = answer(c, cp, GOOD)
    assert first.status_code == 200 and first.json()['status'] == 'passed'
    assert answer(c, cp, GOOD).json()['status'] == 'passed'
    assert model.answer_calls == 1
    assert answer(c, cp, 'Different answer same key').status_code == 409
    assert answer(c, cp, GOOD, 'new-stale-key').status_code == 409


def test_outage_retry_and_restart(app_env):
    c, _, db, model, config = app_env
    _, s = start(c)
    cp = change(c, s).json()['checkpoint']
    model.fail = True
    assert answer(c, cp, GOOD).status_code == 503
    restored = TestClient(create_app(config, db, model), headers=c.headers)
    state = restored.get(f"/v1/checkpoints/{cp['id']}").json()
    assert state['status'] == 'unavailable'
    assert state['attempts'][0]['answer'] == GOOD
    assert restored.get(f"/v1/sessions/{s['id']}/gate").json()['available'] is False
    model.fail = False
    duplicate = change(restored, s).json()['checkpoint']
    assert duplicate['question'] == cp['question'] and duplicate['version'] == cp['version']
    assert model.question_calls == 1
    result = answer(restored, cp, GOOD)
    assert result.status_code == 200, result.text
    assert result.json()['status'] == 'passed'
    assert len(result.json()['attempts']) == 1


def test_question_failure_preserves_lock(app_env):
    c, _, _, model, _ = app_env
    _, s = start(c)
    model.fail = True
    assert change(c, s).status_code == 503
    gate = c.get(f"/v1/sessions/{s['id']}/gate").json()
    assert not gate['available'] and gate['checkpoint_id']
    model.fail = False
    assert c.post(f"/v1/checkpoints/{gate['checkpoint_id']}/retry").status_code == 200


def test_end_restore_and_new_edits_do_not_unlock(app_env):
    c, _, _, _, _ = app_env
    p, s = start(c)
    cp = change(c, s).json()['checkpoint']
    other = c.post(f"/v1/sessions/{s['id']}/changes", json={'files': [{'path': 'src/other.ts', 'before': BEFORE, 'after': AFTER}], 'idempotency_key': 'other-change'})
    assert other.status_code == 409
    assert c.get(f"/v1/checkpoints/{cp['id']}").json()['snapshot_hash'] == cp['snapshot_hash']
    c.post(f"/v1/sessions/{s['id']}/end")
    new = c.post('/v1/sessions', json={'project_id': p['id']}).json()
    assert not c.get(f"/v1/sessions/{new['id']}/gate").json()['available']


def test_owner_isolation_and_auth(app_env):
    c, app, _, _, _ = app_env
    p, s = start(c)
    cp = change(c, s).json()['checkpoint']
    assert c.get('/v1/history', headers={'Authorization': ''}).status_code == 401
    app.dependency_overrides[app.state.auth] = lambda: 'another-owner'
    assert c.get('/v1/history').json() == []
    for url in [f"/v1/checkpoints/{cp['id']}", f"/v1/sessions/{s['id']}/gate", f"/v1/sessions/{s['id']}/history"]:
        assert c.get(url).status_code == 404
    assert c.delete(f"/v1/projects/{p['id']}").status_code == 404
    assert answer(c, cp, GOOD).status_code == 404


def test_pause_after_three_never_passes(app_env):
    c, _, _, _, _ = app_env
    _, s = start(c)
    cp = change(c, s).json()['checkpoint']
    for n in range(3):
        cp = answer(c, cp, 'It is safer.', f'weak-answer-{n}').json()
    assert cp['can_pause']
    assert cp['status'] == 'needs_followup'
    assert not c.get(f"/v1/sessions/{s['id']}/gate").json()['available']


def test_durable_lease_excludes_concurrent_operations(app_env):
    c, _, db, _, _ = app_env
    _, s = start(c)
    with db.transaction() as tx:
        tx.add(Lease(owner='local-developer', token=uid(), expires=time.time()+30))
    assert change(c, s).status_code == 409
    assert not c.get(f"/v1/sessions/{s['id']}/gate").json()['available']


def test_filter_scope_secrets_whitespace_and_no_string_suppression():
    files = [FileChange(path='src/a.ts', before='const x = 1;', after='  const x = 1;\n'),
             FileChange(path='.env.ts', before='', after='const x = 2;'),
             FileChange(path='src/b.ts', before='', after='const api_key = "supersecret123";'),
             FileChange(path='private/c.ts', before='', after='const x = 2;'),
             FileChange(path='src/d.ts', before='const query = "a b";', after='const query = "ab";')]
    result = capture(files, ['src'], [])
    assert len(result['files']) == 1
    assert result['files'][0]['path'] == 'src/d.ts'


def test_delete_cascades_and_never_claims_pass(app_env):
    c, _, _, _, _ = app_env
    p, s = start(c)
    cp = change(c, s).json()['checkpoint']
    answer(c, cp, GOOD)
    r = c.delete(f"/v1/projects/{p['id']}")
    assert r.status_code == 200
    assert not r.json()['learning_pass_issued']
    assert c.get('/v1/history').json() == []


def test_invalid_model_pass_rejected():
    with pytest.raises(ValueError):
        Evaluation(decision='pass', intent_correct=True, mechanism_correct=False, reasoning_correct=True,
            central_contradiction=True, feedback='Good!', evidence=[], gaps=[], next_question=None)


def test_production_rejects_local_auth_and_telemetry_allowlist():
    with pytest.raises(ValueError):
        Settings(_env_file=None, environment='production', auth_mode='local', local_dev_token='x'*40)
    out = scrub_event({'request': {'body': GOOD}, 'exception': {'secret': 'do not log'}, 'message': AFTER, 'tags': {'operation': 'evaluation', 'code': BEFORE}})
    assert GOOD not in str(out) and AFTER not in str(out) and BEFORE not in str(out)
    out = scrub_log({'body': AFTER, 'attributes': {'operation': 'question', 'answer': GOOD}})
    assert GOOD not in str(out) and AFTER not in str(out)


def test_untrusted_origin_and_invalid_input_redaction(app_env):
    c, _, _, _, _ = app_env
    assert c.post('/v1/projects', headers={'Origin': 'https://attacker.example'}, json={'name': 'bad', 'scope': ['.']}).status_code == 403
    result = c.post('/v1/projects', json={'name': 'secret answer', 'scope': []})
    assert result.status_code == 422 and 'secret answer' not in result.text


def test_large_edit_has_partial_context_and_template_whitespace_is_meaningful():
    big = capture([FileChange(path='src/large.ts', before='', after='\n'.join(f'export const x{i} = {i};' for i in range(400)))], ['src'], [])
    assert big['partial'] and big['files'] and big['changed_lines'] <= 200 and big['context_lines'] <= 300
    template = capture([FileChange(path='src/a.ts', before='const x = `hello\n world`;', after='const x = `hello\n  world`;')], ['src'], [])
    assert template['files']


def test_scope_update_is_versioned_and_enforced_before_assessment(app_env):
    c,_,_,model,_=app_env
    p,s=start(c)
    payload={'name':p['name'],'scope':['src/utils'],'exclusions':[],'expected_scope_hash':p['scope_hash']}
    updated=c.post(f"/v1/projects/{p['id']}/scope",json=payload)
    assert updated.status_code==200
    assert c.post(f"/v1/projects/{p['id']}/scope",json=payload).status_code==200
    assert c.post(f"/v1/projects/{p['id']}/scope",json={**payload,'scope':['src/private']}).status_code==409
    assert change(c,s).json()['status']=='skipped'
    assert model.question_calls==0


def test_interrupted_evaluation_can_be_reconciled_after_lease_expiry(app_env):
    c,_,db,_,_=app_env
    _,s=start(c);cp=change(c,s).json()['checkpoint']
    with db.transaction() as tx:
        row=tx.get(Checkpoint,cp['id']);row.status='evaluating'
        tx.add(Attempt(owner='local-developer',checkpoint_id=cp['id'],key='interrupted-answer',request_hash='0'*64,
            version=cp['version'],answer=GOOD,modality='text',state='evaluating'))
    restored=c.get(f"/v1/checkpoints/{cp['id']}").json()
    assert restored['status']=='unavailable' and restored['attempts'][0]['state']=='failed'
    assert not c.get(f"/v1/sessions/{s['id']}/gate").json()['available']


def test_context_expiry_preserves_result_metadata(app_env):
    from backend.retention import expire_context
    c,_,db,_,_=app_env
    _,s=start(c);cp=answer(c,change(c,s).json()['checkpoint'],GOOD).json()
    with db.transaction() as tx:
        tx.get(Checkpoint,cp['id']).created=time.time()-31*86400
    assert expire_context(db)==1
    saved=c.get(f"/v1/checkpoints/{cp['id']}").json()
    assert saved['snapshot']['files']==[] and saved['snapshot']['expired']
    assert saved['status']=='passed' and saved['attempts'][0]['answer']==GOOD
