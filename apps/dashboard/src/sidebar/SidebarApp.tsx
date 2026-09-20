import {useEffect,useRef,useState} from 'react'
import {ExtensionPanel,type ExtActions} from '../components/ExtensionPanel'
import {Button,InlineNotice} from '../components/ui'
import {initialExtensionState,type Phase} from '../lib/machine'
import {ProductContext,productData} from '../lib/product'
import {passed} from '../lib/api'
import {listen,send,type SidebarState} from './bridge'

export default function SidebarApp(){
  const [state,setState]=useState<SidebarState|null>(null)
  const [text,setText]=useState('')
  const [localError,setLocalError]=useState('')
  const [mode,setMode]=useState<'checkpoint'|'active'|'paused'>('checkpoint')
  const [light,setLight]=useState(document.body.classList.contains('vscode-light'))
  const [elapsed,setElapsed]=useState(0)
  const binding=useRef('')
  useEffect(()=>{
    setElapsed(0)
    if(!state?.busy||['ready','refresh','connect'].includes(state.operation||''))return
    const started=Date.now()
    const timer=setInterval(()=>setElapsed(Math.floor((Date.now()-started)/1000)),1000)
    return()=>clearInterval(timer)
  },[state?.busy,state?.operation])
  useEffect(()=>{
    const stop=listen(next=>{
      const key=next.checkpoint?next.checkpoint.id+':'+next.checkpoint.version:''
      if(key!==binding.current){
        binding.current=key;setText(next.draft?.text||'');setMode('checkpoint');setLocalError('')
      }
      if(next.connected&&!next.error)setLocalError('')
      setState(next)
    })
    void send('ready').catch(e=>setLocalError(e.message))
    const observer=new MutationObserver(()=>setLight(document.body.classList.contains('vscode-light')||document.body.classList.contains('vscode-high-contrast-light')))
    observer.observe(document.body,{attributes:true,attributeFilter:['class']})
    return()=>{stop();observer.disconnect()}
  },[])
  const action=(name:string)=>{setLocalError('');void send(name).catch(e=>setLocalError(e.message))}
  if(!state)return <main className="min-h-screen bg-canvas p-5 text-primary"><p role="status">Loading CodeProof…</p>{localError&&<InlineNotice kind="error">{localError}<Button variant="text" onClick={()=>action('ready')}>Reconnect</Button></InlineNotice>}</main>
  const cp=state.checkpoint
  const stageAttempts=cp?.attempts.filter(a=>!cp.practice_started_version||a.version>=cp.practice_started_version)||[]
  const working=state.busy&&!['ready','refresh'].includes(state.operation||'')
  const offline=!!state.connectionError
  let phase:Phase=!state.session?'welcome':!cp||cp.status==='skipped'?'active':cp.status==='given_up'?'completed':passed(cp)?'verified':cp.status==='unavailable'||!cp.question?'error':cp.status==='evaluating'?'evaluating':cp.status==='needs_followup'?'followup':'checkpoint'
  if(state.session && mode==='active')phase='active'
  if(cp&&!passed(cp)&&mode==='paused')phase='paused'
  if(state.operation==='capture')phase='analyzing'
  if(cp&&(state.operation==='answer'||state.operation==='retry'))phase=stageAttempts.some(a=>a.evaluation?.decision==='follow_up')?'followup-evaluating':'evaluating'
  const updateDraft=(value:string)=>{
    setText(value)
    if(cp)void send('draft',{checkpointId:cp.id,version:cp.version,snapshotHash:cp.snapshot_hash,text:value}).catch(e=>setLocalError(e.message))
  }
  const submit=()=>{
    if(!cp||working)return
    setLocalError('')
    void send('answer',{checkpointId:cp.id,version:cp.version,snapshotHash:cp.snapshot_hash,text}).catch(e=>setLocalError(e.message))
  }
  const actions:ExtActions={
    startPractice:()=>{setMode('checkpoint');action('practice')},
    giveUp:cp?.question?.decision==='assess' ? ()=>{setMode('checkpoint');action('explain')} : undefined,
    connectAccount:()=>action('connect'),continueSetup:()=>action('connect'),startSession:()=>action('connect'),cancelSetup:()=>setMode('active'),
    triggerAiRequest:()=>action('ask'),reviewChanges:()=>{setMode('checkpoint');action('capture')},openCheckpoint:()=>setMode('checkpoint'),
    keepEditing:()=>setMode('active'),submitInitial:submit,submitFollowup:submit,continueCoding:()=>setMode('active'),
    pauseCheckpoint:()=>setMode('paused'),resumeCheckpoint:()=>setMode('checkpoint'),endSession:()=>action('end'),
    retry:()=>action('retry'),reconnect:()=>action('refresh'),setInitialDraft:updateDraft,setFollowupDraft:updateDraft,
    openHistory:()=>action('history'),openSettings:()=>action('settings'),createReceipt:()=>action('receipt')
  }
  const s={...initialExtensionState,phase,accountConnected:state.connected,connection:state.connected?'connected' as const:'disconnected' as const,
    gate:state.gate?.available?'available' as const:'paused' as const,passed:!!cp&&passed(cp),initialDraft:phase.startsWith('followup')?stageAttempts[0]?.answer||'':text,followupDraft:text,showPausedRequestNotice:!!state.session&&!state.gate?.available}
  const fx=productData(state.project,state.session,cp,state.history,state.config)
  // Webview microphone permissions are not a verified capability. Optional voice
  // stays on the website; the complete text checkpoint is local to this sidebar.
  fx.VOICE_ENABLED=false
  fx.ACCOUNT_CONNECT_HINT='Start CodeProof locally, then enter LOCAL_DEV_TOKEN from its .env in the VS Code prompt. This is a local password, not a paid API key. It stays in SecretStorage.'
  return <ProductContext.Provider value={fx}><main className={(light?'light ':'dark ')+'flex min-h-screen flex-col bg-panel text-primary'}>
    <nav aria-label="Sidebar actions" className="flex flex-wrap items-center gap-3 border-b border-subtle px-4 py-2 text-[12px] text-secondary">
      <button disabled={state.busy} onClick={()=>action('refresh')}>Refresh</button>
      {state.connected&&<button disabled={state.busy} onClick={()=>action('projects')}>Projects</button>}
      {state.session&&<button disabled={state.busy||offline||!state.gate?.available} title={state.gate?.available?'Ask the local coding assistant':'Complete the checkpoint to unlock Managed Ask AI'} onClick={()=>action('ask')}>Managed Ask AI</button>}
      <button disabled={state.busy} onClick={()=>action('history')}>Learning history ↗</button>
      {state.connected&&<button disabled={state.busy} onClick={()=>action('disconnect')} className="ml-auto">Disconnect</button>}
    </nav>
    {(state.error||localError)&&<div role="alert" className="p-3"><InlineNotice kind="error">{localError||state.error}{!state.connected&&!offline&&<Button variant="text" onClick={()=>action('connect')}>Connect account</Button>}</InlineNotice></div>}
    {state.notice&&<div role="status" className="px-3 pt-3"><InlineNotice kind="info">{state.notice}</InlineNotice></div>}
    {state.config&&!state.config.capabilities.assessment&&<p className="px-4 pt-3 text-[12px] leading-5 text-secondary">{state.config.ai?.message || 'Start the local model server, then refresh. No API key is required.'}</p>}
    {working&&<p role="status" className="px-4 pt-3 text-[12px] text-secondary">{state.operation==='connect'?'Complete the VS Code connection prompts.':state.operation==='capture'?'Review and approve the saved source preview in VS Code.':'Working… your result is saved before the AI gate changes.'}</p>}
    {working&&elapsed>=10&&<p className="px-4 pt-2 text-[12px] leading-5 text-secondary">{elapsed}s elapsed. {elapsed>=30?'Local processing is taking longer than usual. You can keep editing; the checkpoint stays saved.':'The model runs on this computer. The first request can take longer to load.'}</p>}
    {offline?<section className="space-y-4 p-5" aria-label="Backend offline"><h2 className="text-lg font-semibold">CodeProof is offline</h2><p className="text-sm text-secondary">Start the CodeProof backend, then refresh to reopen your checkpoint. This is a connection problem, not an assessment result.</p>{text&&<div className="whitespace-pre-wrap break-words rounded border border-subtle p-3 text-sm"><p className="mb-2 text-secondary">Your draft (kept in this window)</p>{text}</div>}<Button disabled={state.busy} onClick={()=>action('refresh')}>Refresh connection</Button></section>:<fieldset disabled={working} className="m-0 flex min-w-0 flex-1 flex-col border-0 p-0"><ExtensionPanel s={s} a={actions}/></fieldset>}
    <p className="border-t border-subtle px-4 py-3 text-[11px] leading-[17px] text-secondary">Only CodeProof Managed Ask AI is gated. Manual edits and other assistants remain available. Capture covers approved saved Git changes; unsaved buffers are excluded.</p>
  </main></ProductContext.Provider>
}
