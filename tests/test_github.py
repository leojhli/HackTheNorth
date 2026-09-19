import base64
import pytest
from backend.github import GitHubService, PRInput, SummaryInput, PublishInput
from backend.contracts import ChangeInput
from backend.errors import AppError
from tests.conftest import start, answer, GOOD, BEFORE, AFTER


class FixtureGitHub:
    head = 'a'*40
    published = []
    count = 0
    timeout = False

    def pr(self, owner, repository, number):
        assert repository == 'demo/campus-events' and number == 12
        return {'number':number,'title':'Parameterize query','changed_files':1,'base':{'sha':'b'*40,'repo':{'full_name':repository}},'head':{'sha':self.head,'repo':{'full_name':repository}}}

    def proxy(self, owner, path):
        if '/files?' in path:
            return [{'filename':'src/data/findUser.ts','status':'modified'}]
        code = BEFORE if 'ref='+'b'*40 in path else AFTER
        return {'type':'file','encoding':'base64','size':len(code),'content':base64.b64encode(code.encode()).decode()}

    def comments(self, owner, repository, number):
        return self.published

    def publish(self, owner, repository, number, body):
        self.count += 1
        self.published = [{'id':123,'body':body,'html_url':f'https://github.com/{repository}/pull/{number}#issuecomment-123'}]
        if self.timeout:
            raise AppError('timeout', 'Test-only ambiguous write', 503, True)
        return self.published[0]


def setup(app_env):
    c, app, _, _, _ = app_env
    p,s = start(c)
    adapter = FixtureGitHub();adapter.published=[]
    gh = GitHubService(app.state.service, adapter)
    imported = gh.import_pr('local-developer', PRInput(project_id=p['id'],repository='demo/campus-events',number=12))
    cp = app.state.service.change('local-developer',s['id'],ChangeInput(**imported['capture']))['checkpoint']
    cp = answer(c,cp,GOOD).json()
    preview = gh.preview('local-developer',SummaryInput(checkpoint_ids=[cp['id']]))
    return gh,adapter,preview,cp,c,s


def test_exact_preview_and_uncertain_write_reconciles_once(app_env):
    gh,adapter,preview,cp,c,s=setup(app_env)
    assert GOOD not in preview['body'] and BEFORE not in preview['body']
    data=PublishInput(preview_id=preview['id'],approved_digest=preview['digest'],consent=True)
    adapter.timeout=True
    with pytest.raises(AppError,match='publication_uncertain'):
        gh.publish('local-developer',data)
    result=gh.publish('local-developer',data)
    assert result['state']=='published' and adapter.count==1
    assert c.get(f"/v1/sessions/{s['id']}/gate").json()['available']


def test_stale_head_wrong_owner_and_preview_tamper(app_env):
    gh,adapter,preview,cp,_,_=setup(app_env)
    with pytest.raises(AppError,match='preview_mismatch'):
        gh.publish('local-developer',PublishInput(preview_id=preview['id'],approved_digest='0'*64,consent=True))
    with pytest.raises(AppError,match='not_found'):
        gh.publish('other-owner',PublishInput(preview_id=preview['id'],approved_digest=preview['digest'],consent=True))
    adapter.head='c'*40
    with pytest.raises(AppError,match='stale_pr_head'):
        gh.publish('local-developer',PublishInput(preview_id=preview['id'],approved_digest=preview['digest'],consent=True))
    assert adapter.count==0
