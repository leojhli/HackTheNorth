const path=require('node:path');
const crypto=require('node:crypto');
const {collect,git,within}=require('./capture.cjs');
const {validateMessage}=require('./protocol.cjs');
const PASSING=new Set(['passed','passed_with_help']);

class Controller {
  constructor(vscode,context,onState=()=>{}) {
    this.vscode=vscode;this.context=context;this.onState=onState;
    this.active=null;this.checkpoint=null;this.draft=null;this.answerIntent=null;this.askIntent=null;
    this.state={connected:false,project:null,session:null,checkpoint:null,gate:null,history:[],config:null,busy:false,operation:null,error:'',notice:'',draft:null};
  }
  origin() {
    const url=new URL(this.vscode.workspace.getConfiguration('beprogram').get('apiUrl'));
    if(url.username||url.password||url.search||url.hash||url.pathname!=='/' ||
      (url.protocol!=='https:' && !(url.protocol==='http:' && ['localhost','127.0.0.1','[::1]'].includes(url.hostname))))
      throw Error('Set beprogram.apiUrl to an HTTPS origin or a loopback HTTP origin, without a path or credentials.');
    return url.origin;
  }
  emit() {this.onState({...this.state,draft:this.draft});}
  trusted() {
    if(!this.vscode.workspace.isTrusted) throw Error('Trust this workspace before connecting or capturing source.');
  }
  async request(route,method='GET',body,publicRequest=false) {
    const origin=this.origin();
    if(this.active && this.active.origin!==origin) throw Error('Server changed. Reconnect this workspace before continuing.');
    const token=publicRequest?'':await this.context.secrets.get('beprogram.token:'+origin);
    if(!publicRequest&&!token)throw Error('Connect your account first. Your token stays in VS Code SecretStorage.');
    let response;
    try {response=await fetch(origin+route,{method,headers:{...(token?{Authorization:'Bearer '+token}:{}),...(body?{'Content-Type':'application/json'}:{})},body:body?JSON.stringify(body):undefined,redirect:'error',signal:AbortSignal.timeout(135000)});}
    catch {throw Error('Cannot reach BeProgram. Check the backend address, then refresh to reconcile saved work.');}
    const value=await response.json().catch(()=>({}));
    if(!response.ok) {
      if(response.status===401){this.state.connected=false;}
      throw Object.assign(Error(value.message||'BeProgram request failed. Refresh to reconcile.'),{code:value.code});
    }
    return value;
  }
  async remember() {await this.context.workspaceState.update('beprogram.session',this.active);}
  async restore() {
    this.trusted();
    const saved=this.context.workspaceState.get('beprogram.session');
    if(!saved)return;
    if(saved.origin!==this.origin())return;
    const roots=this.vscode.workspace.workspaceFolders||[];
    if(!roots.some(folder=>path.relative(saved.root,folder.uri.fsPath)==='' || within(saved.root,folder.uri.fsPath)))return;
    this.active=saved;
    await this.refresh();
  }
  async refresh() {
    this.trusted();
    this.state.config=await this.request('/v1/config','GET',undefined,true);
    if(!this.active){this.emit();return;}
    const [projects,sessions,history]=await Promise.all([this.request('/v1/projects'),this.request('/v1/sessions'),this.request('/v1/history')]);
    const project=projects.find(p=>p.id===this.active.projectId);
    const session=sessions.find(s=>s.id===this.active.sessionId);
    if(!project || !session || session.status!=='active') {
      this.active=null;await this.remember();
      Object.assign(this.state,{connected:true,project:project||null,session:null,checkpoint:null,gate:null,history:[]});
      this.checkpoint=null;this.draft=null;this.emit();return;
    }
    const gate=await this.request('/v1/sessions/'+session.id+'/gate');
    let cp=gate.checkpoint_id ? await this.request('/v1/checkpoints/'+gate.checkpoint_id) : null;
    if(!cp)cp=history.find(c=>c.id===this.checkpoint?.id) || history.find(c=>c.project_id===project.id&&PASSING.has(c.status)) || null;
    const changed=cp?.id!==this.checkpoint?.id || cp?.version!==this.checkpoint?.version;
    this.checkpoint=cp;
    if(changed || !this.draft) {
      const failed=cp?.attempts.find(a=>a.version===cp.version&&a.state!=='completed');
      this.draft=cp?{checkpointId:cp.id,version:cp.version,snapshotHash:cp.snapshot_hash,text:failed?.answer||''}:null;
      this.answerIntent=failed?{checkpointId:cp.id,version:cp.version,text:failed.answer,key:failed.key,modality:failed.modality}:null;
    }
    Object.assign(this.state,{connected:true,project,session,checkpoint:cp,gate,history:history.filter(c=>c.project_id===project.id)});
    this.emit();
  }
  async connect() {
    this.trusted();
    const folders=this.vscode.workspace.workspaceFolders;
    if(!folders?.length)throw Error('Open a local Git repository folder first.');
    const folder=folders.length===1?folders[0]:await this.vscode.window.showWorkspaceFolderPick();
    if(!folder)return;
    if(folder.uri.scheme!=='file')throw Error('This extension currently supports local Git repositories.');
    const root=path.resolve((await git(folder.uri.fsPath,'rev-parse','--show-toplevel')).trim());
    const origin=this.origin();
    const token=await this.vscode.window.showInputBox({password:true,ignoreFocusOut:true,prompt:'BeProgram access token (LOCAL_DEV_TOKEN or Supabase access token). Stored only in VS Code SecretStorage.'});
    if(!token)return;
    // Reset all previous-account content before using another identity.
    this.active=null;this.checkpoint=null;this.draft=null;this.answerIntent=null;this.askIntent=null;
    await this.remember();
    Object.assign(this.state,{connected:false,project:null,session:null,checkpoint:null,gate:null,history:[]});this.emit();
    await this.context.secrets.store('beprogram.token:'+origin,token);
    const projects=await this.request('/v1/projects');
    const selected=await this.vscode.window.showQuickPick([...projects.map(project=>({label:project.name,description:project.scope.join(', '),project})),{label:'$(add) Create project',create:true}],{title:'Choose the approved project for this Git repository'});
    if(!selected)return;
    let project=selected.project;
    if(selected.create) {
      const name=await this.vscode.window.showInputBox({prompt:'Project name',value:path.basename(root),ignoreFocusOut:true});
      if(!name)return;
      const paths=await this.vscode.window.showInputBox({prompt:'Approved relative files/directories, separated by commas',value:'src',ignoreFocusOut:true});
      if(!paths)return;
      project=await this.request('/v1/projects','POST',{name,scope:paths.split(',').map(x=>x.trim()).filter(Boolean),exclusions:[]});
    }
    const consent=await this.vscode.window.showInformationMessage('Start BeProgram for '+project.name+'? Scope: '+project.scope.join(', ')+'. Saved source uploads require a separate preview approval. Only Managed Ask AI is gated.',{modal:true},'Start session');
    if(consent!=='Start session')return;
    const session=await this.request('/v1/sessions','POST',{project_id:project.id});
    this.active={root,origin,projectId:project.id,sessionId:session.id};
    await this.remember();await this.refresh();
  }
  async capture() {
    this.trusted();
    if(!this.active)throw Error('Connect and start a scoped session first.');
    await this.refresh();
    if(!this.active)throw Error('The session ended. Connect again before capture.');
    const payload=await collect(this.active.root,this.state.project);
    payload.idempotency_key=crypto.createHash('sha256').update(this.active.sessionId+':'+payload.idempotency_key).digest('hex');
    if(!payload.files.length){this.state.notice='No eligible saved changes in the approved scope.';return;}
    const doc=await this.vscode.workspace.openTextDocument({language:'json',content:JSON.stringify(payload,null,2)});
    await this.vscode.window.showTextDocument(doc,{preview:true,preserveFocus:true});
    const consent=await this.vscode.window.showInformationMessage('Send the exact previewed saved changes to your local BeProgram model? No hosted AI is used. Unsaved buffers are excluded.',{modal:true},'Approve capture');
    if(consent!=='Approve capture')throw Error('Capture cancelled. Nothing was uploaded and no AI request was sent.');
    const result=await this.request('/v1/sessions/'+this.active.sessionId+'/changes','POST',payload);
    if(result.checkpoint){if(this.checkpoint?.id!==result.checkpoint.id)this.draft=null;this.checkpoint=result.checkpoint;}
    this.state.notice=result.status==='skipped'?(result.reason||result.checkpoint?.question?.reason||'No checkpoint needed for this change.'):'';
    await this.refresh();
  }
  bound(payload) {
    const cp=this.checkpoint;
    if(!cp || payload.checkpointId!==cp.id || payload.version!==cp.version || payload.snapshotHash!==cp.snapshot_hash)
      throw Error('This question changed. Refresh before submitting your explanation.');
    return cp;
  }
  async answer(payload) {
    const cp=this.bound(payload);
    if(PASSING.has(cp.status))throw Error('This checkpoint is already saved as passed.');
    this.draft={...payload};
    if(!this.answerIntent || this.answerIntent.checkpointId!==cp.id || this.answerIntent.version!==cp.version || this.answerIntent.text!==payload.text)
      this.answerIntent={checkpointId:cp.id,version:cp.version,text:payload.text,key:crypto.randomUUID(),modality:'text'};
    const result=await this.request('/v1/checkpoints/'+cp.id+'/answers','POST',{answer:payload.text,version:cp.version,snapshot_hash:cp.snapshot_hash,idempotency_key:this.answerIntent.key,modality:this.answerIntent.modality});
    this.checkpoint=result;this.draft=null;this.answerIntent=null;await this.refresh();
  }
  async retry() {
    await this.refresh();
    const cp=this.checkpoint;
    if(!cp)throw Error('No checkpoint to retry.');
    if(!cp.question || cp.question.decision==='unable_to_assess') {
      this.checkpoint=await this.request('/v1/checkpoints/'+cp.id+'/retry','POST');
      await this.refresh();
    } else {
      const failed=cp.attempts.find(a=>a.version===cp.version && a.state!=='completed');
      const text=this.draft?.text||failed?.answer;
      if(!text)throw Error('Write an explanation before retrying.');
      await this.answer({checkpointId:cp.id,version:cp.version,snapshotHash:cp.snapshot_hash,text});
    }
  }
  async ask() {
    await this.capture(); // Always reconcile local saved changes before a controlled request.
    await this.refresh();
    if(!this.state.gate?.available)throw Error('Explain the unresolved checkpoint in this sidebar before the next Managed Ask AI request.');
    const prompt=await this.vscode.window.showInputBox({prompt:'Managed Ask AI — suggestions open in a document; no files are edited automatically.',ignoreFocusOut:true});
    if(!prompt)return;
    if(!this.askIntent || this.askIntent.prompt!==prompt || this.askIntent.session!==this.active.sessionId)
      this.askIntent={prompt,session:this.active.sessionId,key:crypto.randomUUID()};
    const result=await this.request('/v1/sessions/'+this.active.sessionId+'/ask','POST',{prompt,idempotency_key:this.askIntent.key});
    const doc=await this.vscode.workspace.openTextDocument({language:'markdown',content:result.text});
    await this.vscode.window.showTextDocument(doc,{preview:false});
    this.askIntent=null;this.state.notice='AI response opened in the editor. Capture resulting saved changes before the next request.';
  }
  async openDashboard(destination) {
    const route=destination==='settings'?'/settings':destination==='receipt'&&this.checkpoint?'/history/'+encodeURIComponent(this.checkpoint.id):'/history';
    await this.vscode.env.openExternal(this.vscode.Uri.parse(this.origin()+route));
  }
  async execute(action,payload) {
    if(action==='draft') {this.bound(payload);this.draft={...payload};return;}
    if(this.state.busy)throw Error('An operation is already running. Wait for its saved result.');
    this.state.busy=true;this.state.operation=action;this.state.error='';this.state.notice='';this.emit();
    try {
      switch(action) {
        case 'ready': if(!this.active)await this.restore();await this.refresh();break;
        case 'refresh': await this.refresh();break;
        case 'connect': await this.connect();break;
        case 'capture': await this.capture();break;
        case 'answer': await this.answer(payload);break;
        case 'retry': await this.retry();break;
        case 'ask': await this.ask();break;
        case 'end': {
          const confirmed=await this.vscode.window.showWarningMessage('End this session? Unresolved checkpoints remain unresolved.',{modal:true},'End session');
          if(confirmed==='End session'&&this.active) {
            await this.request('/v1/sessions/'+this.active.sessionId+'/end','POST');await this.refresh();
          }
          break;
        }
        case 'disconnect': {
          await this.context.secrets.delete('beprogram.token:'+this.origin());
          this.active=null;this.checkpoint=null;this.draft=null;this.answerIntent=null;this.askIntent=null;await this.remember();
          Object.assign(this.state,{connected:false,project:null,session:null,checkpoint:null,gate:null,history:[]});break;
        }
        case 'history':case 'settings':case 'receipt':await this.openDashboard(action);break;
        default:throw Error('Unsupported sidebar action.');
      }
    } catch(error) {
      const message=error.message;
      if(this.active && !['refresh','ready','draft'].includes(action))await this.refresh().catch(()=>{});
      this.state.error=message;throw error;
    } finally {this.state.busy=false;this.state.operation=null;this.emit();}
  }
  async receive(message) {
    if(!validateMessage(message))return {id:typeof message?.id==='string'?message.id.slice(0,80):'',ok:false,error:'Invalid sidebar message.'};
    if(message.action==='ready'&&this.state.busy){this.emit();return {id:message.id,ok:true};}
    try{await this.execute(message.action,message.payload);return {id:message.id,ok:true};}
    catch(error){return {id:message.id,ok:false,error:error.message};}
  }
}
module.exports={Controller};
