import { useEffect, useRef, useState } from 'react'
import { useProduct } from '../lib/product'
import { api } from '../lib/api'
import { Button, InlineNotice, TextArea } from './ui'

export function SpeechPlayback({text}:{text:string}) {
  const fx=useProduct(); const [busy,setBusy]=useState(false);const [error,setError]=useState('');const audio=useRef<HTMLAudioElement|null>(null);const url=useRef('')
  const generation=useRef(0)
  const stop=()=>{generation.current++;audio.current?.pause();audio.current=null;if(url.current)URL.revokeObjectURL(url.current);url.current='';setBusy(false)}
  useEffect(()=>()=>{generation.current++;audio.current?.pause();if(url.current)URL.revokeObjectURL(url.current)},[])
  if(!fx.VOICE_ENABLED)return null
  return <div><button aria-label={busy?'Stop playback':'Listen to question'} className="rounded-[var(--radius-control)] p-1.5 text-[12px] text-action hover:bg-raised" onClick={async()=>{if(busy){stop();return}const current=++generation.current;setBusy(true);setError('');try{const blob=await api<Blob>(`/v1/checkpoints/${fx.CHECKPOINT_ID}/speech`,'POST',{text});if(current!==generation.current)return;url.current=URL.createObjectURL(blob);audio.current=new Audio(url.current);audio.current.onended=stop;await audio.current.play()}catch(e){if(current!==generation.current)return;stop();setError((e as Error).message)}}}>{busy?'Stop':'Listen'}</button>{error&&<span role="status" className="text-[12px] text-error">{error}</span>}</div>
}

export function VoiceAnswer({onTranscript}:{onTranscript:(s:string)=>void}) {
  const fx=useProduct();const [stage,setStage]=useState<'ready'|'permission'|'recording'|'transcribing'|'review'|'error'>('ready');const [seconds,setSeconds]=useState(0);const [transcript,setTranscript]=useState('');const [error,setError]=useState('')
  const generation=useRef(0)
  const recorder=useRef<MediaRecorder|null>(null);const stream=useRef<MediaStream|null>(null);const timer=useRef<ReturnType<typeof setInterval>|null>(null);const cancelFlag=useRef(false)
  const cleanup=()=>{stream.current?.getTracks().forEach(t=>t.stop());if(timer.current)clearInterval(timer.current)}
  const cancel=()=>{generation.current++;cancelFlag.current=true;if(recorder.current?.state==='recording')recorder.current.stop();cleanup();setStage('ready')}
  useEffect(()=>()=>{generation.current++;cancelFlag.current=true;if(recorder.current?.state==='recording')recorder.current.stop();cleanup()},[])
  if(!fx.VOICE_ENABLED)return null
  async function start() {
    const current=++generation.current
    try{cancelFlag.current=false;setError('');setStage('permission');const media=await navigator.mediaDevices.getUserMedia({audio:true});if(current!==generation.current){media.getTracks().forEach(t=>t.stop());return}stream.current=media;const rec=new MediaRecorder(media);recorder.current=rec;const chunks:BlobPart[]=[];let bytes=0
      rec.ondataavailable=e=>{bytes+=e.data.size;if(bytes>10_000_000){cancelFlag.current=true;rec.stop();cleanup();setError('Recording exceeded 10 MB. Try a shorter explanation.');setStage('error')}else chunks.push(e.data)}
      rec.onstop=async()=>{if(current!==generation.current)return;cleanup();if(cancelFlag.current)return;setStage('transcribing');try{const form=new FormData();form.append('audio',new Blob(chunks,{type:rec.mimeType}),'answer.webm');form.append('checkpoint_id',fx.CHECKPOINT_ID);const r=await api<{text:string}>('/v1/audio/transcriptions','POST',form);if(current!==generation.current)return;setTranscript(r.text);setStage('review')}catch(e){if(current!==generation.current)return;setError((e as Error).message);setStage('error')}}
      setSeconds(0);setStage('recording');rec.start(1000);let elapsed=0;timer.current=setInterval(()=>{elapsed++;setSeconds(elapsed);if(elapsed>=90&&rec.state==='recording')rec.stop()},1000)
    }catch(e){if(current!==generation.current)return;cleanup();setError('Microphone unavailable or permission denied. You can type your explanation.');setStage('error')}
  }
  if(stage==='ready')return <div className="space-y-1"><Button variant="secondary" onClick={()=>void start()}>Record answer</Button><p className="text-[11px] text-secondary">Up to 90 seconds. Audio goes to ElevenLabs for transcription; review the text before submission.</p></div>
  if(stage==='recording')return <div className="flex flex-wrap items-center gap-3 rounded-[var(--radius-panel)] border border-subtle bg-canvas p-3"><span role="status" className="text-[13px] text-error">● Recording · {seconds}s / 90s</span><Button onClick={()=>recorder.current?.stop()}>Stop</Button><Button variant="secondary" onClick={cancel}>Cancel</Button></div>
  if(stage==='transcribing'||stage==='permission')return <div className="flex items-center gap-3"><p role="status" className="text-[13px] text-secondary">{stage==='permission'?'Waiting for microphone permission…':'Preparing your transcript… Typed answers remain available.'}</p><Button variant="secondary" onClick={cancel}>Cancel</Button></div>
  if(stage==='review')return <div className="space-y-2 rounded-[var(--radius-panel)] border border-subtle bg-canvas p-3"><TextArea label="Review your transcript before submitting" value={transcript} onChange={e=>setTranscript(e.target.value)}/><Button disabled={!transcript.trim()} onClick={()=>{onTranscript(transcript);setStage('ready')}}>Use this transcript</Button><Button variant="text" onClick={()=>setStage('ready')}>Discard</Button></div>
  return <InlineNotice kind="info">{error} <button onClick={()=>setStage('ready')} className="underline">Try recording again</button></InlineNotice>
}
