import type {Checkpoint,Config,Gate,Project,Session} from '../lib/api'
export type Draft={checkpointId:string;version:number;snapshotHash:string;text:string}
export type SidebarState={connectionError?:boolean;connected:boolean;project:Project|null;session:Session|null;checkpoint:Checkpoint|null;gate:Gate|null;history:Checkpoint[];config:Config|null;busy:boolean;operation:string|null;error:string;notice:string;draft:Draft|null}
declare function acquireVsCodeApi(): {postMessage:(message:unknown)=>void}
const host=acquireVsCodeApi()
const pending=new Map<string,{resolve:()=>void;reject:(error:Error)=>void;timer:ReturnType<typeof setTimeout>}>()
const listeners=new Set<(state:SidebarState)=>void>()
window.addEventListener('message',event=>{
  const message=event.data
  if(message?.type==='state'&&message.state)listeners.forEach(listener=>listener(message.state))
  if(message?.type==='result'&&typeof message.id==='string'){
    const request=pending.get(message.id)
    if(!request)return
    clearTimeout(request.timer);pending.delete(message.id)
    if(message.ok)request.resolve();else request.reject(new Error(message.error||'Extension request failed.'))
  }
})
export function listen(listener:(state:SidebarState)=>void){listeners.add(listener);return()=>{listeners.delete(listener)}}
export function send(action:string,payload?:Draft):Promise<void>{
  const id=crypto.randomUUID()
  return new Promise((resolve,reject)=>{
    const timer=setTimeout(()=>{pending.delete(id);reject(new Error('The extension has not responded. Refresh to reconcile; no passing result is assumed.'))},180000)
    pending.set(id,{resolve,reject,timer})
    host.postMessage({id,action,...(payload?{payload}:{})})
  })
}
