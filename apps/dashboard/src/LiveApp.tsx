import { useEffect, useRef, useState } from 'react'
import { createClient, type SupabaseClient } from '@supabase/supabase-js'
import { ExtensionPanel, type ExtActions } from './components/ExtensionPanel'
import { LiveWebsite } from './components/LiveWebsite'
import { Button, InlineNotice, Modal, TextArea, Wordmark } from './components/ui'
import { Sun, Moon, Refresh } from './lib/icons'
import { initialExtensionState, type Phase } from './lib/machine'
import { api, setToken, passed, type Config, type Project, type Session, type Checkpoint, type Gate } from './lib/api'
import { ProductContext, productData } from './lib/product'
import { ReceiptFlow, VerifierPage, PRImportDialog, PRSummaryDialog } from './components/Optional'

export default function LiveApp() {
  const [route, setRoute] = useState(location.pathname)
  const [config, setConfig] = useState<Config | null>(null)
  const [authReady, setAuthReady] = useState(false)
  const [dark, setDark] = useState(localStorage.getItem('beprogram-theme') !== 'light')
  const [projects, setProjects] = useState<Project[]>([])
  const [project, setProject] = useState<Project | null>(null)
  const [session, setSession] = useState<Session | null>(null)
  const [history, setHistory] = useState<Checkpoint[]>([])
  const [cp, setCp] = useState<Checkpoint | null>(null)
  const [gate, setGate] = useState<Gate | null>(null)
  const [s, setS] = useState(initialExtensionState)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [dialog, setDialog] = useState<'project' | 'capture' | 'ask' | 'end' | 'receipt' | 'pr' | 'summary' | null>(null)
  const [selectedEvidence, setSelectedEvidence] = useState<Checkpoint | null>(null)
  const [captureJson, setCaptureJson] = useState('')
  const [prompt, setPrompt] = useState('')
  const [aiResponse, setAiResponse] = useState('')
  const [projectName, setProjectName] = useState('')
  const [scope, setScope] = useState('src')
  const [exclusions, setExclusions] = useState('')
  const supabase = useRef<SupabaseClient | null>(null)
  const answerKey = useRef<{ text: string; version: number; key: string } | null>(null)
  const askKey = useRef<{text: string; key: string} | null>(null)
  const requestBusy = useRef(false)
  const answerModality = useRef('text')
  const navigate = (path: string) => { window.history.pushState({}, '', path); setRoute(path) }
  const patch = (value: Partial<typeof s>) => setS(prev => ({ ...prev, ...value }))
  useEffect(() => { const pop = () => setRoute(location.pathname); addEventListener('popstate', pop); return () => removeEventListener('popstate', pop) }, [])
  useEffect(() => { localStorage.setItem('beprogram-theme', dark ? 'dark' : 'light') }, [dark])
  useEffect(() => {
    let unsubscribe: (() => void) | undefined
    api<Config>('/v1/config').then(c => {
      setConfig(c)
      if (c.auth_mode === 'local') { const token = sessionStorage.getItem('beprogram-local-token'); if (token) { setToken(token); setAuthReady(true) } }
      else if (c.supabase_url && c.supabase_publishable_key) {
        const client = createClient(c.supabase_url, c.supabase_publishable_key); supabase.current = client
        const { data } = client.auth.onAuthStateChange((_event, session) => { setToken(session?.access_token || ''); setAuthReady(!!session) })
        unsubscribe = () => data.subscription.unsubscribe()
      }
    }).catch(e => setError(e.message))
    return () => unsubscribe?.()
  }, [])

  function showCheckpoint(next: Checkpoint | null, nextGate?: Gate) {
    setCp(next)
    if (!next) { patch({ phase: 'active', passed: false, gate: nextGate?.available ? 'available' : 'paused', showPausedRequestNotice: false }); return }
    const phase: Phase = passed(next) ? 'verified' : next.status === 'unavailable' || !next.question ? 'error' : next.status === 'evaluating' ? 'evaluating' : next.status === 'needs_followup' ? 'followup' : 'checkpoint'
    const retry = next.attempts.find(a=>a.version===next.version && a.state!=='completed')
    if(retry) answerKey.current={text:retry.answer,version:retry.version,key:retry.key}
    answerModality.current = retry?.modality || 'text'
    patch({ phase, passed: passed(next), gate: nextGate?.available ? 'available' : 'paused', initialDraft: next.attempts[0]?.answer || '', followupDraft: retry && next.attempts.length>1 ? retry.answer : '', showPausedRequestNotice: !passed(next) })
  }
  async function refresh(open = false) {
    const [ps, sessions, hs, freshConfig] = await Promise.all([api<Project[]>('/v1/projects'), api<Session[]>('/v1/sessions'), api<Checkpoint[]>('/v1/history'), api<Config>('/v1/config')])
    setConfig(freshConfig)
    setProjects(ps); setHistory(hs)
    const active = sessions.find(x => x.status === 'active') || null
    const selected = ps.find(p => p.id === active?.project_id) || ps.find(p => p.id === project?.id) || ps[0] || null
    setProject(selected); setSession(active); patch({ accountConnected: true, connection: 'connected' })
    if (active) {
      const g = await api<Gate>(`/v1/sessions/${active.id}/gate`); setGate(g)
      const next = g.checkpoint_id ? hs.find(x => x.id === g.checkpoint_id) || await api<Checkpoint>(`/v1/checkpoints/${g.checkpoint_id}`) : cp ? hs.find(x => x.id === cp.id) || null : null
      if (open) showCheckpoint(next, g)
      else { setCp(next); patch({ gate: g.available ? 'available' : 'paused', showPausedRequestNotice: !g.available }) }
    } else { setGate(null); if (open) patch({ phase: 'welcome' }) }
  }
  useEffect(() => { if (authReady) void run(() => refresh(true)) }, [authReady])
  useEffect(() => {
    if (!authReady || !session) return
    const timer = setInterval(() => { if (!requestBusy.current) void refresh(false).catch(e => { setError(e.message); patch({ connection: 'disconnected' }) }) }, 8000)
    return () => clearInterval(timer)
  }, [authReady, session?.id, cp?.id])
  async function run(task: () => Promise<void>) {
    if (requestBusy.current) return
    requestBusy.current = true; setBusy(true); setError('')
    try { await task() } catch (e) { setError(e instanceof Error ? e.message : 'Request failed. Refresh to reconcile.'); }
    finally { requestBusy.current = false; setBusy(false) }
  }
  async function submitAnswer() {
    if (!cp) return
    const text = s.phase.startsWith('followup') ? s.followupDraft : s.followupDraft || s.initialDraft
    if (!answerKey.current || answerKey.current.text !== text || answerKey.current.version !== cp.version) answerKey.current = {text, version: cp.version, key: crypto.randomUUID()}
    patch({phase: s.phase.startsWith('followup') ? 'followup-evaluating' : 'evaluating'})
    try {
      const next = await api<Checkpoint>(`/v1/checkpoints/${cp.id}/answers`, 'POST', {answer: text, version: cp.version, snapshot_hash: cp.snapshot_hash, idempotency_key: answerKey.current.key, modality: answerModality.current})
      const g = session ? await api<Gate>(`/v1/sessions/${session.id}/gate`) : undefined; setGate(g || null); showCheckpoint(next, g)
      setHistory(await api<Checkpoint[]>('/v1/history')); answerKey.current = null
    } catch(e) { patch({phase: 'error'}); throw e }
  }
  const a: ExtActions = {
    connectAccount: () => {}, continueSetup: () => { if (project) patch({phase:'scope'}); else setDialog('project') },
    startSession: () => void run(async () => { if (!project) return; const next = await api<Session>('/v1/sessions','POST',{project_id:project.id}); setSession(next); const g = await api<Gate>(`/v1/sessions/${next.id}/gate`); setGate(g); showCheckpoint(g.checkpoint_id ? await api(`/v1/checkpoints/${g.checkpoint_id}`) : null,g) }),
    cancelSetup: () => patch({phase:'welcome'}), triggerAiRequest: () => { setDialog('ask'); setAiResponse('') },
    reviewChanges: () => setDialog('capture'), openCheckpoint: () => { if(cp) showCheckpoint(cp,gate || undefined) }, keepEditing: () => patch({phase:'active'}),
    submitInitial: () => void run(submitAnswer), submitFollowup: () => void run(submitAnswer), continueCoding: () => patch({phase:'active'}),
    pauseCheckpoint: () => patch({phase:'paused'}), resumeCheckpoint: () => showCheckpoint(cp,gate || undefined), endSession: () => setDialog('end'),
    retry: () => void run(async () => { if (cp && (!cp.question || cp.question.decision === 'unable_to_assess')) { const next = await api<Checkpoint>(`/v1/checkpoints/${cp.id}/retry`,'POST'); showCheckpoint(next,gate || undefined) } else await submitAnswer() }),
    reconnect: () => void run(() => refresh(true)), setInitialDraft: initialDraft => patch({initialDraft}), setFollowupDraft: followupDraft => patch({followupDraft}),
    setInitialVoiceDraft: initialDraft => { answerModality.current='reviewed_voice'; patch({initialDraft}) },
    setFollowupVoiceDraft: followupDraft => { answerModality.current='reviewed_voice'; patch({followupDraft}) },
    openHistory: () => navigate('/history'), openSettings: () => navigate('/settings'), createReceipt: () => { setSelectedEvidence(cp); setDialog('receipt') },
  }
  return <ProductContext.Provider value={productData(project,session,cp,history,config)}><div className={dark ? 'dark':'light'}><div className="flex min-h-screen flex-col bg-canvas text-primary">
    <header className="sticky top-0 z-40 border-b border-subtle bg-panel/85 px-4 py-2.5 backdrop-blur"><div className="mx-auto flex max-w-[1440px] flex-wrap items-center gap-x-4 gap-y-2">
      <Wordmark size="sm"/><nav aria-label="Main navigation" className="flex items-center gap-1 rounded-full bg-canvas p-0.5">{[['/','Checkpoint'],['/history','Website'],['/settings','Settings'],...(config?.capabilities.receipts ? [['/verify','Verifier']] : [])].map(([url,label]) => <button key={url} onClick={()=>navigate(url)} className={`rounded-full px-3 py-1 text-[12px] ${route===url?'bg-action text-on-action':'text-secondary hover:text-primary'}`}>{label}</button>)}</nav>
      <div className="ml-auto flex items-center gap-2"><button aria-label="Refresh saved state" onClick={()=>void run(()=>refresh(true))} disabled={busy || !authReady}><Refresh size={15}/></button><button aria-label="Toggle theme" onClick={()=>setDark(!dark)}>{dark?<Sun size={15}/>:<Moon size={15}/>}</button>{authReady && <Button variant="text" onClick={()=>{void supabase.current?.auth.signOut(); sessionStorage.removeItem('beprogram-local-token'); setToken(''); setAuthReady(false); setHistory([]); setProjects([]); setProject(null); setGate(null); setSelectedEvidence(null); setDialog(null); setCp(null); setSession(null)}}>Sign out</Button>}</div>
    </div></header>
    <main className="flex-1 p-3 sm:p-5"><div className="mx-auto max-w-[1200px] space-y-4">
      {error && <div role="alert"><InlineNotice kind="error">{error} <button className="underline" onClick={()=>setError('')}>Dismiss</button></InlineNotice></div>}
      {notice && <div role="status"><InlineNotice kind="info">{notice}</InlineNotice></div>}
      {busy && <p role="status" className="text-[13px] text-secondary">Working… your saved state remains on the server.</p>}
      {route==='/verify' ? (config?.capabilities.receipts ? <VerifierPage onBack={()=>navigate('/history')}/> : <InlineNotice kind="info">Receipts are disabled for the core demo. <button className="underline" onClick={()=>navigate('/history')}>Return to learning history</button></InlineNotice>) : !authReady ? <SignIn config={config} client={supabase.current} onLocal={token=>{sessionStorage.setItem('beprogram-local-token',token);setToken(token);setAuthReady(true)}} onError={setError}/> : <>
        {config && !config.capabilities.assessment && <InlineNotice kind="info">{config.ai?.message || 'Start the local model server to assess changes. No API key is needed.'}</InlineNotice>}
        {route.startsWith('/history') || route==='/settings' ? <LiveWebsite route={route} navigate={navigate} project={project} history={history} config={config} busy={busy} refresh={()=>void run(()=>refresh(false))} onCheckpoint={checkpoint=>{showCheckpoint(checkpoint,gate || undefined);navigate('/')}} onReceipt={checkpoint=>{setSelectedEvidence(checkpoint);setDialog('receipt')}} onImport={()=>setDialog('pr')} onSummary={checkpoint=>{setSelectedEvidence(checkpoint);setDialog('summary')}} onDelete={()=>void run(async()=>{if(project) await api(`/v1/projects/${project.id}`,'DELETE');setProject(null);setCp(null);setSession(null);await refresh(true);navigate('/history')})}/> : <>
          {!session && <div className="flex flex-wrap items-end gap-3 rounded-[var(--radius-panel)] border border-subtle bg-panel p-4"><label className="text-[13px]">Project<select aria-label="Project" value={project?.id || ''} onChange={e=>{setProject(projects.find(p=>p.id===e.target.value)||null);patch({phase:'scope'})}} className="ml-3 rounded border border-control bg-canvas p-2"><option value="">Choose a project</option>{projects.map(p=><option key={p.id} value={p.id}>{p.name}</option>)}</select></label><Button variant="secondary" onClick={()=>setDialog('project')}>New project</Button></div>}
          <div className="mx-auto min-h-[520px] max-w-[860px] overflow-hidden rounded-[var(--radius-dialog)] border border-subtle shadow-2xl"><ExtensionPanel s={{...s,accountConnected:authReady}} a={a}/></div>
          <p className="mx-auto max-w-[860px] text-[12px] leading-5 text-secondary">Managed Ask AI is controlled by BeProgram. Other assistants remain available. The website assesses approved uploaded changes; use the companion for saved Git changes. Unsaved buffers and unsubmitted edits are outside this checkpoint.</p>
          {cp?.snapshot.partial && <InlineNotice kind="pending">Partial coverage: this checkpoint covers only the captured bounded excerpt.</InlineNotice>}
        </>}
      </>}
    </div></main>
    {dialog==='project' && <Modal onClose={()=>setDialog(null)}><div className="space-y-4"><h2 className="text-[18px] font-semibold">Start with an approved project</h2><Field label="Project name" value={projectName} onChange={setProjectName}/><Field label="Included paths (comma separated)" value={scope} onChange={setScope}/><Field label="Excluded paths (comma separated)" value={exclusions} onChange={setExclusions}/><InlineNotice kind="info">Only saved JavaScript/TypeScript in these paths is eligible. Secrets, ignored files and generated output are excluded before upload by the companion.</InlineNotice><Button loading={busy} disabled={!projectName.trim()||!scope.trim()} onClick={()=>void run(async()=>{const p=await api<Project>('/v1/projects','POST',{name:projectName,scope:scope.split(',').map(s=>s.trim()).filter(Boolean),exclusions:exclusions.split(',').map(s=>s.trim()).filter(Boolean)});setProjects([...projects,p]);setProject(p);patch({phase:'scope'});setDialog(null)})}>Create project</Button></div></Modal>}
    {dialog==='capture' && <Modal onClose={()=>setDialog(null)}><div className="space-y-4"><h2 className="text-[18px] font-semibold">Review saved changes</h2><p className="text-[13px] text-secondary">Preview the companion capture JSON, then explicitly send the approved files to your local BeProgram model. This does not change Git staging.</p><label className="block text-[13px]">Load capture JSON<input className="mt-2 block max-w-full" type="file" accept="application/json,.json" onChange={async e=>{const file=e.target.files?.[0];if(file && file.size<2_000_000)setCaptureJson(await file.text());else setError('Choose a JSON file under 2 MB.')}}/></label><TextArea label="Approved capture JSON" value={captureJson} onChange={e=>setCaptureJson(e.target.value)} className="min-h-[220px] font-mono"/><p className="text-[12px] text-secondary">Shape: files with path, before, after; provenance. Use the local capture companion for filtered saved snapshots.</p><Button loading={busy} disabled={!captureJson.trim()||!session} onClick={()=>void run(async()=>{const input=JSON.parse(captureJson);if(input.blocked?.length)throw new Error('The capture contains blocked files. Narrow the scope first.');patch({phase:'analyzing'});try{const result=await api(`/v1/sessions/${session!.id}/changes`,'POST',{files:input.files,provenance:input.provenance||'unknown',pr_import_id:input.pr_import_id||null,idempotency_key:input.idempotency_key||crypto.randomUUID()});setDialog(null);setNotice(result.status==='skipped'?result.reason || result.checkpoint?.question?.reason:'');await refresh(true)}catch(e){patch({phase:'error'});await refresh(true);throw e}})}>Approve capture and generate question</Button></div></Modal>}
    {dialog==='ask' && <Modal onClose={()=>setDialog(null)}><div className="space-y-4"><h2 className="text-[18px] font-semibold">Managed Ask AI</h2>{!gate?.available && <InlineNotice kind="pending">A checkpoint is unresolved. Complete it before your next managed request.</InlineNotice>}<TextArea label="Coding request" value={prompt} onChange={e=>setPrompt(e.target.value)} className="min-h-[150px]"/><p className="text-[12px] text-secondary">Responses appear here. BeProgram does not edit your files. Capture resulting changes before your next request.</p><Button loading={busy} disabled={!gate?.available||prompt.trim().length<3} onClick={()=>void run(async()=>{if(askKey.current?.text!==prompt)askKey.current={text:prompt,key:crypto.randomUUID()};const result=await api(`/v1/sessions/${session!.id}/ask`,'POST',{prompt,idempotency_key:askKey.current.key});setAiResponse(result.text)})}>Send AI request</Button>{aiResponse && <pre className="max-h-[350px] overflow-auto whitespace-pre-wrap rounded border border-subtle bg-canvas p-3 text-[13px]">{aiResponse}</pre>}</div></Modal>}
    {dialog==='end' && <Modal onClose={()=>setDialog(null)}><h2 className="text-[18px] font-semibold">End this session?</h2><p className="my-4 text-[13px] text-secondary">Submitted explanations remain saved. Unresolved checkpoints stay unresolved for this project.</p><Button variant="destructive" loading={busy} onClick={()=>void run(async()=>{await api(`/v1/sessions/${session!.id}/end`,'POST');setSession(null);patch({phase:'welcome'});setDialog(null)})}>End session</Button></Modal>}
    {dialog==='receipt' && selectedEvidence && <ReceiptFlow checkpoint={selectedEvidence} onClose={()=>setDialog(null)} onOpenVerifier={()=>{setDialog(null);navigate('/verify')}}/>}
    {dialog==='pr' && project && <PRImportDialog project={project} onClose={()=>setDialog(null)} onImport={async files=>{if(!session){try{setSession(await api<Session>('/v1/sessions','POST',{project_id:project.id}))}catch(e){setError((e as Error).message);return}}setCaptureJson(JSON.stringify(files,null,2));setDialog('capture')}}/>}
    {dialog==='summary' && selectedEvidence && <PRSummaryDialog checkpoint={selectedEvidence} onClose={()=>setDialog(null)}/>}
  </div></div></ProductContext.Provider>
}

export function Field({label,value,onChange,type='text'}:{label:string;value:string;onChange:(s:string)=>void;type?:string}) { return <label className="block text-[13px] font-medium">{label}<input required type={type} value={value} onChange={e=>onChange(e.target.value)} className="mt-1.5 block w-full rounded-[var(--radius-control)] border border-control bg-canvas px-3 py-2 text-[14px]"/></label> }
function SignIn({config,client,onLocal,onError}:{config:Config|null;client:SupabaseClient|null;onLocal:(t:string)=>void;onError:(s:string)=>void}) {
  const [email,setEmail]=useState('');const [password,setPassword]=useState('');const [waiting,setWaiting]=useState(false)
  const local=config?.auth_mode==='local'
  return <form onSubmit={async e=>{e.preventDefault();setWaiting(true);try{if(local){setToken(password);await api('/v1/projects');onLocal(password)}else if(client){const r=await client.auth.signInWithPassword({email,password});if(r.error)throw r.error}else throw new Error('Configure Supabase URL and publishable key on the server.')}catch(e){onError(e instanceof Error?e.message:'Sign-in failed')}finally{setWaiting(false)}}} className="mx-auto mt-10 max-w-[520px] space-y-5 rounded-[var(--radius-panel)] border border-subtle bg-panel p-6"><h1 className="text-[22px] font-semibold">Understand what you build</h1><p className="text-[14px] leading-[22px] text-secondary">Connect your account to start a scoped coding session. Your explanations and learning history stay private.</p>{!config?<p>Loading authentication…</p>:<>{local?<InlineNotice kind="info">Local development identity. Enter the token configured in your local .env file.</InlineNotice>:<Field label="Email" type="email" value={email} onChange={setEmail}/>}<Field label={local?'Local development token':'Password'} type="password" value={password} onChange={setPassword}/><Button type="submit" loading={waiting}>Connect account</Button>{!local&&<p className="text-[12px] text-secondary">Use an account created in your configured Supabase project.</p>}</>}</form>
}
