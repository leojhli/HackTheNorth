const vscode=require('vscode');
const fs=require('node:fs');
const path=require('node:path');
const crypto=require('node:crypto');
const {Controller}=require('./controller.cjs');
const {within}=require('./capture.cjs');

function html(webview,extensionUri) {
  const nonce=crypto.randomBytes(24).toString('base64');
  const asset=name=>webview.asWebviewUri(vscode.Uri.joinPath(extensionUri,'media',name)).toString();
  const csp="default-src 'none'; script-src 'nonce-"+nonce+"'; style-src "+webview.cspSource+" 'unsafe-inline'; font-src "+webview.cspSource+"; img-src "+webview.cspSource+" data:; connect-src 'none'; form-action 'none'; base-uri 'none';";
  return '<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="'+csp+'"><link rel="stylesheet" href="'+asset('webview.css')+'"><title>CodeProof checkpoint</title></head><body><div id="root"></div><script nonce="'+nonce+'" src="'+asset('webview.js')+'"></script></body></html>';
}
function activate(context) {
  let view=null,saveTimer=null,pollTimer=null,ready=false;
  const status=vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left,15);
  status.command='codeproof.open';status.text='CodeProof: not started';status.show();
  const controller=new Controller(vscode,context,state=>{
    status.text=state.connectionError?'CodeProof: backend offline':!state.session?'CodeProof: not started':state.busy?'CodeProof: working':state.gate?.available?'CodeProof: AI available':'CodeProof: checkpoint required';
    if(view&&ready)void view.webview.postMessage({type:'state',state});
  });
  const provider={
    resolveWebviewView(resolved) {
      view=resolved;ready=false;
      view.webview.options={enableScripts:true,localResourceRoots:[vscode.Uri.joinPath(context.extensionUri,'media')]};
      if(!fs.existsSync(path.join(context.extensionPath,'media','webview.js'))) {
        view.webview.html='<html><body><p>Build the CodeProof sidebar first: run scripts/build-extension.ps1 from the repository root.</p></body></html>';return;
      }
      view.webview.html=html(view.webview,context.extensionUri);
      const receive=view.webview.onDidReceiveMessage(async message=>{
        if(message?.action==='ready')ready=true;
        const result=await controller.receive(message);
        await resolved.webview.postMessage({type:'result',...result});
      });
      const visibility=view.onDidChangeVisibility(()=>{
        if(view?.visible&&!controller.state.busy)void controller.execute('refresh').catch(()=>{});
      });
      const disposed=view.onDidDispose(()=>{receive.dispose();visibility.dispose();disposed.dispose();if(view===resolved){view=null;ready=false;}});
      context.subscriptions.push(receive,visibility,disposed);
    }
  };
  context.subscriptions.push(status,vscode.window.registerWebviewViewProvider('codeproof.checkpoint',provider,{webviewOptions:{retainContextWhenHidden:false}}));
  const focus=()=>vscode.commands.executeCommand('codeproof.checkpoint.focus');
  const command=(name,action)=>context.subscriptions.push(vscode.commands.registerCommand(name,async()=>{
    await focus();
    try{await controller.execute(action);}catch(error){void vscode.window.showErrorMessage(error.message);}
  }));
  context.subscriptions.push(vscode.commands.registerCommand('codeproof.open',focus));
  command('codeproof.connect','connect');command('codeproof.capture','capture');command('codeproof.ask','ask');
  command('codeproof.stop','end');command('codeproof.refresh','refresh');command('codeproof.projects','projects');command('codeproof.disconnect','disconnect');command('codeproof.history','history');
  context.subscriptions.push(vscode.workspace.onDidChangeConfiguration(event=>{
    if(event.affectsConfiguration('codeproof.apiUrl')) {
      controller.active=null;controller.checkpoint=null;controller.draft=null;
      Object.assign(controller.state,{connected:false,session:null,project:null,checkpoint:null,gate:null,history:[],error:'Backend address changed. Connect this workspace to the selected server.'});
      controller.emit();
    }
  }));
  context.subscriptions.push(vscode.workspace.onDidSaveTextDocument(doc=>{
    if(!controller.active || doc.uri.scheme!=='file' || !within(controller.active.root,doc.uri.fsPath))return;
    clearTimeout(saveTimer);
    saveTimer=setTimeout(async()=>{
      if(controller.state.busy)return;
      const choice=await vscode.window.showInformationMessage('Saved changes are ready for a CodeProof checkpoint preview.','Review changes');
      if(choice)void vscode.commands.executeCommand('codeproof.capture');
    },5000);
  }));
  pollTimer=setInterval(()=>{if(view?.visible&&ready&&!controller.state.busy)void controller.execute('refresh').catch(()=>{});},8000);
  context.subscriptions.push({dispose(){clearInterval(pollTimer);clearTimeout(saveTimer);}});
  void controller.execute('ready').catch(()=>{});
  return {controller,provider,getView:()=>view,isReady:()=>ready};
}
module.exports={activate};
