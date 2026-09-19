const vscode=require('vscode');
const assert=require('node:assert/strict');
const fs=require('node:fs/promises');
const path=require('node:path');
const crypto=require('node:crypto');
const TOKEN='automated-test-only-token-not-a-real-secret';
const GOOD='The query structure is fixed. The driver binds email as data, so quotes in email cannot change SQL syntax. Input validation is still needed for business rules.';
const wait=ms=>new Promise(resolve=>setTimeout(resolve,ms));

exports.run=async()=>{
  const results=[];
  const root=vscode.workspace.workspaceFolders[0].uri.fsPath;
  await vscode.workspace.getConfiguration('codeproof').update('apiUrl','http://127.0.0.1:8011',vscode.ConfigurationTarget.Global);
  const extension=vscode.extensions.getExtension('codeproof-local.codeproof-companion');
  assert(extension,'Installed development extension was discovered');
  const api=await extension.activate();
  const {Controller}=require(path.join(extension.extensionPath,'controller.cjs'));
  const controller=api.controller;
  const originalVscode=controller.vscode;
  let approve=true,external=0;
  // Only native consent/token prompts are automated; documents, VS Code webview,
  // SecretStorage, Git capture and the real FastAPI routes execute normally.
  controller.vscode=Object.create(vscode,{
    window:{value:Object.create(vscode.window,{
      showInformationMessage:{value:async()=>approve?'Approve capture':undefined},
      showInputBox:{value:async()=> 'Write a safe helper'}
    })},
    env:{value:Object.create(vscode.env,{openExternal:{value:async()=>{external++;return true;}}})}
  });
  try{
    await controller.context.secrets.store('codeproof.token:http://127.0.0.1:8011',TOKEN);
    const call=async(route,body)=>{
      const response=await fetch('http://127.0.0.1:8011'+route,{method:body?'POST':'GET',headers:{Authorization:'Bearer '+TOKEN,'Content-Type':'application/json'},body:body?JSON.stringify(body):undefined});
      assert(response.ok,await response.clone().text());return response.json();
    };
    const project=await call('/v1/projects',{name:'VS Code integration fixture',scope:['src']});
    const session=await call('/v1/sessions',{project_id:project.id});
    await controller.context.workspaceState.update('codeproof.session',{root,origin:'http://127.0.0.1:8011',projectId:project.id,sessionId:session.id});
    await controller.execute('ready');
    await vscode.commands.executeCommand('codeproof.open');
    for(let n=0;n<100&&!api.getView();n++)await wait(100);
    assert(api.getView(),'Real VS Code WebviewView was created');
    for(let n=0;n<100&&!api.isReady();n++)await wait(100);
    assert(api.isReady(),'Built React sidebar completed the webview message handshake');
    while(controller.state.busy)await wait(50);
    results.push('Extension activation, real sidebar creation and React/host handshake');
    const html=api.getView().webview.html;
    assert(html.includes("connect-src 'none'")&&html.includes("script-src 'nonce-"));
    assert(!html.includes(TOKEN));
    assert.equal(api.getView().webview.options.localResourceRoots.length,1);
    results.push('CSP, local resource scope and no bearer token in webview HTML');

    approve=false;
    await assert.rejects(controller.execute('capture'),/cancelled/);
    assert.equal((await call('/v1/history')).length,0);
    approve=true;
    await controller.execute('capture');
    let cp=controller.state.checkpoint;
    assert(cp?.question);assert.equal(controller.state.gate.available,false);
    assert(vscode.workspace.textDocuments.some(d=>d.languageId==='json'&&d.getText().includes('src/findUser.ts')));
    results.push('Git capture preview/cancel/approval and persisted pending checkpoint');

    const submit=text=>controller.receive({id:crypto.randomUUID(),action:'answer',payload:{checkpointId:cp.id,version:cp.version,snapshotHash:cp.snapshot_hash,text}});
    const stale=await controller.receive({id:'stale',action:'answer',payload:{checkpointId:cp.id,version:cp.version+1,snapshotHash:cp.snapshot_hash,text:GOOD}});
    assert.equal(stale.ok,false);assert.equal((await call('/v1/history'))[0].attempts.length,0);
    assert((await submit('It makes the database safer.')).ok);
    cp=controller.state.checkpoint;assert.equal(cp.status,'needs_followup');
    const restored=new Controller(controller.vscode,controller.context);
    await restored.execute('ready');assert.equal(restored.state.checkpoint.status,'needs_followup');
    assert.equal(restored.state.gate.available,false);
    results.push('Version rejection, adaptive follow-up and extension-controller restart recovery');

    assert((await submit(GOOD)).ok);
    cp=controller.state.checkpoint;
    assert.equal(cp.status,'passed');assert.equal(controller.state.gate.available,true);
    const history=await call('/v1/history');assert.equal(history[0].attempts.length,2);
    await controller.execute('ask');
    assert(vscode.workspace.textDocuments.some(d=>d.languageId==='markdown'&&d.getText().includes('Test-only coding assistant response.')&&d.getText().includes('Approved saved excerpts: src/findUser.ts')));
    assert.equal(external,0,'Checkpoint interaction did not open a browser');
    results.push('Persisted pass, matching dashboard history and next managed AI response inside editor');

    await controller.execute('disconnect');
    assert.equal(await controller.context.secrets.get('codeproof.token:http://127.0.0.1:8011'),undefined);
    assert.equal(controller.state.checkpoint,null);
    results.push('SecretStorage disconnect and private-state clearing');
    await fs.writeFile(path.join(process.env.CODEPROOF_TEST_RUN,'host-results.json'),JSON.stringify({passed:results.length,results,provider:'Explicit test-only assessor; no live model call'},null,2));
    console.log('CODEPROOF_HOST_TESTS_PASSED '+results.length);
  }finally{controller.vscode=originalVscode;}
};
