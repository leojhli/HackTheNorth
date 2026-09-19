import {test,expect} from '@playwright/test'
import {createRequire} from 'node:module'
import {readFile,mkdtemp,mkdir,writeFile} from 'node:fs/promises'
import {execFileSync} from 'node:child_process'
import path from 'node:path'
import os from 'node:os'
const require=createRequire(import.meta.url)
const {Controller}=require('../../vscode-extension/controller.cjs')
const token='automated-test-only-token-not-a-real-secret'
const good='The query structure is fixed. The driver binds email as data, so quotes in email cannot change SQL syntax. Input validation is still needed for business rules.'
const before='export async function findUser(db, email) {\n  return db.query('+String.fromCharCode(96)+'SELECT * FROM users WHERE email = "'+'$'+'{email}"'+String.fromCharCode(96)+');\n}'
const after='export async function findUser(db, email) {\n  return db.query("SELECT * FROM users WHERE email = $1", [email]);\n}'

test('sidebar UI: saved capture, draft restoration, follow-up, pass and next managed request',async({page,request,baseURL})=>{
  const root=await mkdtemp(path.join(os.tmpdir(),'beprogram-sidebar-'))
  await mkdir(path.join(root,'src'));await writeFile(path.join(root,'src/findUser.ts'),before)
  const git=(...args:string[])=>execFileSync('git',['-C',root,...args],{windowsHide:true,stdio:'pipe'})
  git('init');git('add','.');git('-c','user.name=Fixture','-c','user.email=fixture@example.test','commit','-m','fixture')
  await writeFile(path.join(root,'src/findUser.ts'),after)
  const headers={Authorization:'Bearer '+token}
  for(const session of await (await request.get('/v1/sessions',{headers})).json())
    if(session.status==='active')await request.post('/v1/sessions/'+session.id+'/end',{headers})
  const project=await (await request.post('/v1/projects',{headers,data:{name:'Sidebar fixture',scope:['src']}})).json()
  const session=await (await request.post('/v1/sessions',{headers,data:{project_id:project.id}})).json()
  const memory=new Map<string,unknown>([['beprogram.session',{root,origin:baseURL,projectId:project.id,sessionId:session.id}]])
  const documents:{content:string}[]=[];let openedBrowser=false
  const vscode={workspace:{isTrusted:true,workspaceFolders:[{uri:{fsPath:root,scheme:'file'}}],getConfiguration:()=>({get:()=> baseURL}),
    openTextDocument:async(doc:{content:string})=>{documents.push(doc);return doc}},
    window:{showTextDocument:async()=>{},showInformationMessage:async()=> 'Approve capture',showInputBox:async()=> 'Write a safe helper'},
    env:{openExternal:async()=>{openedBrowser=true}},Uri:{parse:(value:string)=>value}}
  const context={workspaceState:{get:(key:string)=>memory.get(key),update:async(key:string,value:unknown)=>memory.set(key,value)},
    secrets:{get:async()=>token,delete:async()=>{}}}
  const controller=new Controller(vscode,context,(state:unknown)=>{if(!page.isClosed())void page.evaluate(state=>window.postMessage({type:'state',state},'*'),state).catch(()=>{})})
  const errors:string[]=[];page.on('pageerror',error=>errors.push(error.message))
  await page.exposeFunction('testExtensionPost',async(message:unknown)=>{
    const result=await controller.receive(message)
    if(!page.isClosed())await page.evaluate(result=>window.postMessage({type:'result',...result},'*'),result)
  })
  await page.addInitScript(()=>{(window as any).acquireVsCodeApi=()=>({postMessage:(message:unknown)=>(window as any).testExtensionPost(message)})})
  const media=path.resolve('..','vscode-extension','media')
  // Read bundle bytes before fulfilling, so no runtime provider simulation enters the UI.
  const css=await readFile(path.join(media,'webview.css'),'utf8')
  const js=await readFile(path.join(media,'webview.js'),'utf8')
  await page.route('**/sidebar-test.js',route=>route.fulfill({contentType:'text/javascript',body:js}))
  await page.route('**/sidebar-test.css',route=>route.fulfill({contentType:'text/css',body:css}))
  await page.route('**/sidebar-test',route=>route.fulfill({contentType:'text/html',body:'<!doctype html><html><head><meta charset="utf-8"><meta http-equiv="Content-Security-Policy" content="default-src \'none\'; script-src \'nonce-test\'; style-src \'self\' \'unsafe-inline\'; connect-src \'none\';"><link rel="stylesheet" href="/sidebar-test.css"></head><body class="vscode-dark"><div id="root"></div><script nonce="test" src="/sidebar-test.js"></script></body></html>'}))
  try{
    await page.setViewportSize({width:360,height:1000})
    await page.goto('/sidebar-test')
    await expect(page.getByRole('heading',{name:'Session active'})).toBeVisible()
    await page.getByRole('button',{name:'Review current changes',exact:true}).click()
    await expect(page.getByRole('heading',{name:'SQL parameterization'})).toBeVisible()
    expect(documents.some(d=>d.content.includes('src/findUser.ts'))).toBeTruthy()
    expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy()
    await page.getByLabel('Your explanation',{exact:true}).fill('Draft preserved while the webview reloads.')
    await expect.poll(()=>controller.draft?.text).toBe('Draft preserved while the webview reloads.')
    await page.reload()
    await expect(page.getByLabel('Your explanation',{exact:true})).toHaveValue('Draft preserved while the webview reloads.')
    await page.screenshot({path:'test-results/vscode-sidebar-checkpoint.png',fullPage:true,animations:'disabled'})
    await page.setViewportSize({width:800,height:1000})
    await page.evaluate(()=>document.body.className='vscode-light')
    expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy()
    await page.screenshot({path:'test-results/vscode-sidebar-light-wide.png',fullPage:true,animations:'disabled'})
    await page.setViewportSize({width:360,height:1000})
    await page.evaluate(()=>document.body.className='vscode-dark')
    await page.getByLabel('Your explanation',{exact:true}).fill('It makes the database safer.')
    await page.getByRole('button',{name:'Submit explanation',exact:true}).click()
    await expect(page.getByRole('heading',{name:'One detail to clarify'})).toBeVisible()
    await page.getByRole('button',{name:'Pause checkpoint',exact:true}).click()
    await expect(page.getByRole('button',{name:'Resume checkpoint',exact:true})).toBeVisible()
    expect(controller.state.gate.available).toBe(false)
    await page.getByRole('button',{name:'Resume checkpoint',exact:true}).click()
    await page.getByLabel('Your follow-up answer').fill(good)
    await page.getByRole('button',{name:'Submit follow-up',exact:true}).click()
    await expect(page.getByRole('heading',{name:'Understanding verified'})).toBeVisible()
    await expect(page.getByText('Saved to your learning history.')).toBeVisible()
    await page.screenshot({path:'test-results/vscode-sidebar-verified.png',fullPage:true,animations:'disabled'})
    await page.getByRole('button',{name:'Continue coding',exact:true}).click()
    await page.getByRole('button',{name:'Send AI request',exact:true}).click()
    await expect(page.getByText('AI response opened in the editor. Capture resulting saved changes before the next request.')).toBeVisible()
    expect(documents.some(d=>d.content==='Test-only coding assistant response.')).toBeTruthy()
    expect(openedBrowser).toBe(false)
    expect(errors).toEqual([])
    expect(JSON.stringify(controller.state)).not.toContain(token)
  }finally{await request.post('/v1/sessions/'+session.id+'/end',{headers})}
})
