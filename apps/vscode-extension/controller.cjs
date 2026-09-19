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
    const url=new URL(this.vscode.workspace.getConfiguration('codeproof').get('apiUrl'));
    if(url.username||url.password||url.search||url.hash||url.pathname!=='/' ||
      (url.protocol!=='https:' && !(url.protocol==='http:' && ['localhost','127.0.0.1','[::1]'].includes(url.hostname))))
      throw Error('Set codeproof.apiUrl to an HTTPS origin or a loopback HTTP origin, without a path or credentials.');
    return url.origin;
  }
  emit() {this.onState({...this.state,draft:this.draft});}
  trusted() {
    if(!this.vscode.workspace.isTrusted) throw Error('Trust this workspace before connecting or capturing source.');
  }
  async request(route,method='GET',body,publicRequest=false) {
    const origin=this.origin();
    if(this.active && this.active.origin!==origin) throw Error('Server changed. Reconnect this workspace before continuing.');
    const token=publicRequest?'':await this.context.secrets.get('codeproof.token:'+origin);
    if(!publicRequest&&!token)throw Error('Connect your account first. Your token stays in VS Code SecretStorage.');
    let response;
    try {response=await fetch(origin+route,{method,headers:{...(token?{Authorization:'Bearer '+token}:{}),...(body?{'Content-Type':'application/json'}:{})},body:body?JSON.stringify(body):undefined,redirect:'error',signal:AbortSignal.timeout(135000)});}
    catch {
      this.state.connected=false;this.state.connectionError=true;
      throw Object.assign(Error('CodeProof backend is offline. Start scripts/run-local.ps1 in the CodeProof folder, then click Refresh. Your saved history and current draft are kept.'),{code:'backend_offline'});
    }
    const value=await response.json().catch(()=>({}));
    if(!response.ok) {
      if(response.status===401){this.state.connected=false;}
      throw Object.assign(Error(value.message||'CodeProof request failed. Refresh to reconcile.'),{code:value.code});
    }
    return value;
  }
  async remember() {await this.context.workspaceState.update('codeproof.session',this.active);}
  async connectionProjects() {
    const key='codeproof.token:'+this.origin();
    if(await this.context.secrets.get(key)) {
      try{return await this.request('/v1/projects');}
      catch(error){if(error.code!=='unauthorized')throw error;await this.context.secrets.delete(key);}
    }
    const token=await this.vscode.window.showInputBox({password:true,ignoreFocusOut:true,prompt:'CodeProof local password: copy the value of LOCAL_DEV_TOKEN from the backend .env. No paid API key is needed. Stored in VS Code SecretStorage.'});
    if(!token)return null;
    await this.context.secrets.store(key,token);
    try{return await this.request('/v1/projects');}
    catch(error){if(error.code==='unauthorized')await this.context.secrets.delete(key);throw error;}
  }
  async restore() {
    this.trusted();
    const saved=this.context.workspaceState.get('codeproof.session');
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
    if(!this.active){this.state.connectionError=false;this.emit();return;}
    const [projects,sessions,history]=await Promise.all([this.request('/v1/projects'),this.request('/v1/sessions'),this.request('/v1/history')]);
    const project=projects.find(p=>p.id===this.active.projectId);
    const session=sessions.find(s=>s.id===this.active.sessionId);
    if(!project || !session || session.status!=='active') {
      this.active=null;await this.remember();
      Object.assign(this.state,{connected:true,project:project||null,session:null,checkpoint:null,gate:null,history:[]});
      this.checkpoint=null;this.draft=null;this.state.connectionError=false;this.emit();return;
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
    Object.assign(this.state,{connected:true,connectionError:false,project,session,checkpoint:cp,gate,history:history.filter(c=>c.project_id===project.id)});
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
    // Reset all previous-account content before using another identity.
    this.active=null;this.checkpoint=null;this.draft=null;this.answerIntent=null;this.askIntent=null;
    await this.remember();
    Object.assign(this.state,{connected:false,project:null,session:null,checkpoint:null,gate:null,history:[]});this.emit();
    const projects=await this.connectionProjects();
    if(!projects)return;
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
    const consent=await this.vscode.window.showInformationMessage('Start CodeProof for '+project.name+'? Scope: '+project.scope.join(', ')+'. Saved source uploads require a separate preview approval. Only Managed Ask AI is gated.',{modal:true},'Start session');
    if(consent!=='Start session')return;
    const session=await this.request('/v1/sessions','POST',{project_id:project.id});
    this.active={root,origin,projectId:project.id,sessionId:session.id};
    await this.remember();await this.refresh();
  }
  async projects() {
    this.trusted();
    const folders=this.vscode.workspace.workspaceFolders;
    if(!folders?.length)throw Error('Open a local Git repository folder first.');
    const folder=folders.length===1?folders[0]:await this.vscode.window.showWorkspaceFolderPick();
    if(!folder)return;
    if(folder.uri.scheme && folder.uri.scheme!=='file')throw Error('This extension currently supports local Git repositories.');
    const root=this.active?.root||path.resolve((await git(folder.uri.fsPath,'rev-parse','--show-toplevel')).trim());
    const origin=this.origin();
    while(true) {
      const projects=await this.connectionProjects();
      if(!projects)return;
      const items=projects.map(project=>({
        label:(project.id===this.active?.projectId?'$(check) ':'')+project.name,
        description:project.scope.join(', '),
        detail:project.id===this.active?.projectId?'Current project':'Saved CodeProof project',
        project
      }));
      items.push({label:'$(add) Create project',description:'Add a saved CodeProof project',create:true});
      if(projects.length)items.push({label:'$(trash) Delete a saved project…',description:'Remove its CodeProof sessions and learning history only',remove:true});
      const selected=await this.vscode.window.showQuickPick(items,{title:'CodeProof projects — choose, create, or delete'});
      if(!selected)return;
      if(selected.remove) {
        const target=await this.vscode.window.showQuickPick(projects.map(project=>({label:project.name,description:project.scope.join(', '),project})),{title:'Delete a project from CodeProof'});
        if(!target)return;
        const [sessions,history]=await Promise.all([this.request('/v1/sessions'),this.request('/v1/history')]);
        const savedSessions=sessions.filter(session=>session.project_id===target.project.id);
        const checkpoints=history.filter(checkpoint=>checkpoint.project_id===target.project.id);
        const answers=checkpoints.reduce((total,checkpoint)=>total+(checkpoint.attempts?.length||0),0);
        const active=target.project.id===this.active?.projectId;
        const sourceNote=active
          ? 'The source folder '+root+' will not be deleted or changed.'
          : 'No project source folder will be deleted or changed.';
        const detail='This permanently removes '+savedSessions.length+' saved session(s), '+checkpoints.length+' learning-history checkpoint(s), and '+answers+' submitted answer(s) for '+target.project.name+'. It also removes their captured snapshots, generated questions and feedback, saved explanations/practice, and project-scoped Managed Ask AI records. '+sourceNote;
        const confirmed=await this.vscode.window.showWarningMessage('Delete '+target.project.name+' from CodeProof?',{modal:true,detail},'Delete project');
        if(confirmed!=='Delete project')continue;
        await this.request('/v1/projects/'+encodeURIComponent(target.project.id),'DELETE');
        if(active) {
          this.active=null;this.checkpoint=null;this.draft=null;this.answerIntent=null;this.askIntent=null;
          await this.remember();
          Object.assign(this.state,{connected:true,project:null,session:null,checkpoint:null,gate:null,history:[]});
        }
        this.state.notice='Deleted '+target.project.name+' from CodeProof. Source files were not changed. Choose another saved project or create one.';
        this.emit();
        continue;
      }
      let project=selected.project;
      if(selected.create) {
        const name=await this.vscode.window.showInputBox({prompt:'Project name',value:path.basename(root),ignoreFocusOut:true});
        if(!name)return;
        const paths=await this.vscode.window.showInputBox({prompt:'Approved relative files/directories, separated by commas',value:'src',ignoreFocusOut:true});
        if(!paths)return;
        project=await this.request('/v1/projects','POST',{name,scope:paths.split(',').map(x=>x.trim()).filter(Boolean),exclusions:[]});
      }
      if(project.id===this.active?.projectId) {
        this.state.notice=project.name+' is already the active project.';this.emit();return;
      }
      if(this.active) {
        const confirmSwitch=await this.vscode.window.showWarningMessage('Switch to '+project.name+'?',{modal:true,detail:'The current coding session will end. Its saved checkpoints and history will remain. No source files will be changed.'},'Switch project');
        if(confirmSwitch!=='Switch project')return;
        await this.request('/v1/sessions/'+encodeURIComponent(this.active.sessionId)+'/end','POST');
      }
      const session=await this.request('/v1/sessions','POST',{project_id:project.id});
      this.active={root,origin,projectId:project.id,sessionId:session.id};
      this.checkpoint=null;this.draft=null;this.answerIntent=null;this.askIntent=null;
      await this.remember();await this.refresh();
      this.state.notice='Switched to '+project.name+'. Saved history for other projects is unchanged.';this.emit();return;
    }
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
    const consent=await this.vscode.window.showInformationMessage('Send the exact previewed saved changes to your local CodeProof model? No hosted AI is used. Unsaved buffers are excluded.',{modal:true},'Approve capture');
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
    const prompt=await this.vscode.window.showInputBox({prompt:'Managed Ask AI uses the latest approved saved code excerpts in this project. Unsaved edits are excluded. Suggestions open in a document; files are not edited.',ignoreFocusOut:true});
    if(!prompt)return;
    if(!this.askIntent || this.askIntent.prompt!==prompt || this.askIntent.session!==this.active.sessionId)
      this.askIntent={prompt,session:this.active.sessionId,key:crypto.randomUUID()};
    let result;
    try{result=await this.request('/v1/sessions/'+this.active.sessionId+'/ask','POST',{prompt,idempotency_key:this.askIntent.key});}
    catch(error){if(error.code==='ask_context_changed')this.askIntent=null;throw error;}
    const context=result.context;
    const contextNote=context?.files?.length
      ? 'Approved saved excerpts: '+context.files.join(', ')+'\nCaptured: '+new Date(context.captured_at*1000).toISOString()+'\n'+(context.partial?'Partial context. ':'')+'Unsaved edits and other files were not included.'
      : 'No approved code excerpts were available for this response. It is general advice, not a review of your current files.';
    const doc=await this.vscode.workspace.openTextDocument({language:'markdown',content:'# CodeProof suggestion\n\nAI-generated suggestion. Not executed or verified; it may be incorrect.\n\n'+contextNote+'\n\n---\n\n'+result.text});
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
        case 'practice': {
          const cp=this.checkpoint;
          if(!cp)throw Error('Open a checkpoint first.');
          this.checkpoint=await this.request('/v1/checkpoints/'+cp.id+'/practice','POST',{version:cp.version,snapshot_hash:cp.snapshot_hash});
          this.draft=null;this.answerIntent=null;
          await this.refresh();
          this.state.notice='Fresh practice question ready. Explain this example in your own words; a passing answer will be labeled demonstrated with help.';
          break;
        }
        case 'explain': {
          if(!this.checkpoint)throw Error('Open a checkpoint first.');
          const id=this.checkpoint.id;
          const consent=await this.vscode.window.showInformationMessage('Read an explanation of this saved change? This does not pass the checkpoint or unlock Managed Ask AI. You can return to the question later.',{modal:true},'Give up and explain');
          if(consent!=='Give up and explain')break;
          this.checkpoint=await this.request('/v1/checkpoints/'+id+'/explanation','POST');
          await this.refresh();
          this.state.notice='Explanation saved. This checkpoint remains unresolved; you can return to it when ready.';
          break;
        }
        case 'ready': if(!this.active)await this.restore();await this.refresh();break;
        case 'refresh': await this.refresh();break;
        case 'connect': await this.connect();break;
        case 'projects': await this.projects();break;
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
          await this.context.secrets.delete('codeproof.token:'+this.origin());
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
