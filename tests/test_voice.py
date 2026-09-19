from tests.conftest import start,change,answer,GOOD
from backend.errors import AppError


def test_optional_voice_unavailable_does_not_change_learning(app_env):
    c,_,_,_,_=app_env
    _,s=start(c)
    cp=change(c,s).json()['checkpoint']
    assert c.post(f"/v1/checkpoints/{cp['id']}/speech",json={'text':cp['question']['question']}).status_code==503
    assert c.post(f"/v1/checkpoints/{cp['id']}/speech",json={'text':'Unapproved unrelated text'}).status_code==403
    assert c.get(f"/v1/checkpoints/{cp['id']}").json()['version']==cp['version']
    assert answer(c,cp,GOOD).json()['status']=='passed'
    assert c.get(f"/v1/sessions/{s['id']}/gate").json()['available']


def test_transcription_failure_preserves_typed_path(app_env):
    c,app,_,_,config=app_env
    _,s=start(c);cp=change(c,s).json()['checkpoint']
    result=c.post('/v1/audio/transcriptions',data={'checkpoint_id':cp['id']},files={'audio':('test.webm',b'test','audio/webm')})
    assert result.status_code==503
    assert c.get(f"/v1/checkpoints/{cp['id']}").json()['attempts']==[]


def test_transcript_requires_explicit_review_and_submission(app_env, monkeypatch):
    from backend.voice import ElevenLabs
    c,_,_,_,config=app_env
    config.elevenlabs_api_key='test-only'; config.elevenlabs_voice_id='test-only'
    # Historical route contract exercised only with an explicitly injected test adapter.
    monkeypatch.setattr(ElevenLabs,'ready',lambda self: None)
    monkeypatch.setattr(ElevenLabs,'transcribe',lambda self,content,mime: GOOD)
    _,s=start(c);cp=change(c,s).json()['checkpoint']
    url='/v1/audio/transcriptions'
    assert c.post(url,data={'checkpoint_id':cp['id']},files={'audio':('invalid.txt',b'test','text/plain')}).status_code==415
    result=c.post(url,data={'checkpoint_id':cp['id']},files={'audio':('test.webm',b'test','audio/webm')})
    assert result.json()=={'text':GOOD,'requires_review':True,'submitted':False}
    assert c.get(f"/v1/checkpoints/{cp['id']}").json()['attempts']==[]
    assert not c.get(f"/v1/sessions/{s['id']}/gate").json()['available']
    submitted=c.post(f"/v1/checkpoints/{cp['id']}/answers",json={'answer':GOOD,'version':cp['version'],'snapshot_hash':cp['snapshot_hash'],'idempotency_key':'reviewed-voice-test','modality':'reviewed_voice'})
    assert submitted.json()['attempts'][0]['modality']=='reviewed_voice'
    assert submitted.json()['status']=='passed'
