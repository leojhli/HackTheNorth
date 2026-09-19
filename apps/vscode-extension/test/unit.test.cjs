const test=require('node:test');
const assert=require('node:assert/strict');
const {Controller}=require('../controller.cjs');
const {validateMessage}=require('../protocol.cjs');
const {within}=require('../capture.cjs');
const path=require('node:path');
const draft={checkpointId:'checkpoint-1',version:1,snapshotHash:'a'.repeat(64),text:'My explanation'};
const cp={id:draft.checkpointId,version:1,snapshot_hash:draft.snapshotHash,status:'pending',attempts:[],question:{decision:'assess'}};
function fixture(){
  const secret=new Map([['beprogram.token:http://127.0.0.1:8000','private-test-token']]);
  const memory=new Map();
  const emitted=[];
  const vscode={workspace:{isTrusted:true,workspaceFolders:[{uri:{fsPath:'C:\\repo'}}],getConfiguration:()=>({get:()=> 'http://127.0.0.1:8000'})},window:{},env:{},Uri:{}};
  const context={secrets:{get:async k=>secret.get(k),store:async(k,v)=>secret.set(k,v),delete:async k=>secret.delete(k)},workspaceState:{get:k=>memory.get(k),update:async(k,v)=>memory.set(k,v)}};
  const controller=new Controller(vscode,context,s=>emitted.push(s));
  controller.checkpoint=structuredClone(cp);
  return {controller,vscode,context,emitted};
}
test('connecting another project reuses the server token without another password prompt',async()=>{
  const {controller,vscode}=fixture();let prompts=0;
  vscode.window.showInputBox=async()=>{prompts++;return 'new-token';};
  controller.request=async()=>[{id:'project-1',name:'Existing project'}];
  assert.equal((await controller.connectionProjects()).length,1);
  assert.equal(prompts,0);
});
test('expired stored token prompts once; an outage does not erase the token',async()=>{
  const {controller,vscode,context}=fixture();let prompts=0,calls=0;
  vscode.window.showInputBox=async()=>{prompts++;return 'replacement-token';};
  controller.request=async()=>{if(++calls===1)throw Object.assign(Error('Expired'),{code:'unauthorized'});return [];};
  assert.deepEqual(await controller.connectionProjects(),[]);
  assert.equal(prompts,1);
  assert.equal(await context.secrets.get('beprogram.token:http://127.0.0.1:8000'),'replacement-token');
  controller.request=async()=>{throw Error('Unavailable');};
  await assert.rejects(controller.connectionProjects(),/Unavailable/);
  assert.equal(prompts,1);
  assert.equal(await context.secrets.get('beprogram.token:http://127.0.0.1:8000'),'replacement-token');
});
test('message boundary denies arbitrary URLs, commands, pass assertions and stale-shaped answers',()=>{
  assert(validateMessage({id:'a',action:'answer',payload:draft}));
  for(const message of [
    {id:'a',action:'fetch',payload:{url:'https://attacker.test'}},
    {id:'a',action:'answer',payload:{...draft,passed:true}},
    {id:'a',action:'answer',payload:{...draft,text:'x'.repeat(8001)}},
    {id:'a',action:'answer',payload:{...draft,version:NaN}},
    {id:'a',action:'capture',payload:{approved:true}},
    {id:'a',action:'settings',url:'https://attacker.test'}
  ])assert.equal(validateMessage(message),false);
});
test('repository boundary uses filesystem path semantics, including Windows drive case',()=>{
  const root=path.resolve('test-repository');
  assert(within(root,path.join(root,'src','a.ts')));
  assert(!within(root,path.resolve(root,'..','outside.ts')));
  assert(!within(root,root+'-sibling'+path.sep+'a.ts'));
  if(process.platform==='win32')assert(within(root.toUpperCase(),path.join(root.toLowerCase(),'src','a.ts')));
});
test('stale binding and invalid messages never reach the API',async()=>{
  const {controller}=fixture();let requests=0;
  controller.request=async()=>{requests++;};
  assert.equal((await controller.receive({id:'a',action:'answer',payload:{...draft,version:2}})).ok,false);
  assert.equal((await controller.receive({id:'b',action:'pass'})).ok,false);
  assert.equal(requests,0);
});
test('answer timeout keeps exact idempotency identity and text for retry',async()=>{
  const {controller}=fixture();const requests=[];
  controller.refresh=async()=>{};
  controller.request=async(route,method,body)=>{requests.push(body);throw Error('transport timeout');};
  await assert.rejects(controller.answer(draft));
  await assert.rejects(controller.answer(draft));
  assert.equal(requests[0].idempotency_key,requests[1].idempotency_key);
  assert.equal(controller.draft.text,draft.text);
  await assert.rejects(controller.answer({...draft,text:'Revised explanation'}));
  assert.notEqual(requests[2].idempotency_key,requests[1].idempotency_key);
});
test('busy operations reject duplicate writes and untrusted workspaces reject capture',async()=>{
  const {controller,vscode}=fixture();controller.state.busy=true;
  assert.equal((await controller.receive({id:'x',action:'answer',payload:draft})).ok,false);
  assert.equal((await controller.receive({id:'ready',action:'ready'})).ok,true);
  controller.state.busy=false;vscode.workspace.isTrusted=false;
  await assert.rejects(controller.capture(),/Trust this workspace/);
});
test('backend origin cannot contain credential forwarding, paths or nonlocal HTTP',()=>{
  const {controller,vscode}=fixture();
  for(const url of ['http://example.com','https://user:secret@example.com','https://example.com/path','https://example.com?token=secret']){
    vscode.workspace.getConfiguration=()=>({get:()=>url});
    assert.throws(()=>controller.origin());
  }
});
test('state posted to the webview never includes stored auth token or API client',async()=>{
  const {controller,emitted}=fixture();controller.emit();
  const text=JSON.stringify(emitted);
  assert(!text.includes('private-test-token'));assert(!text.includes('Authorization'));assert(!text.includes('secrets'));
  await controller.execute('disconnect');
  assert.equal(controller.state.connected,false);assert.equal(controller.checkpoint,null);assert.equal(controller.draft,null);
});
