const fs=require('node:fs/promises');
const path=require('node:path');
const {spawn,execFileSync}=require('node:child_process');
const crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..');
const wait=ms=>new Promise(resolve=>setTimeout(resolve,ms));
async function main(){
  const run=path.join(root,'.tools','extension-tests',crypto.randomUUID());
  const workspace=path.join(run,'repository');
  await fs.mkdir(path.join(run,'profile','User'),{recursive:true});
  await fs.writeFile(path.join(run,'profile','User','settings.json'),JSON.stringify({'chat.disableAIFeatures':true,'telemetry.telemetryLevel':'off','workbench.startupEditor':'none','extensions.autoUpdate':false}));
  await fs.mkdir(path.join(workspace,'src'),{recursive:true});
  const before='export async function findUser(db, email) {\n  return db.query('+String.fromCharCode(96)+'SELECT * FROM users WHERE email = "'+'$'+'{email}"'+String.fromCharCode(96)+');\n}';
  const after='export async function findUser(db, email) {\n  return db.query("SELECT * FROM users WHERE email = $1", [email]);\n}';
  await fs.writeFile(path.join(workspace,'src/findUser.ts'),before);
  const git=(...args)=>execFileSync('git',['-C',workspace,...args],{windowsHide:true,stdio:'pipe'});
  git('init');git('add','.');git('-c','user.name=Test fixture','-c','user.email=fixture@example.test','commit','-m','test fixture');
  await fs.writeFile(path.join(workspace,'src/findUser.ts'),after);
  const python=process.env.CODEPROOF_TEST_PYTHON||path.join(root,'.venv',process.platform==='win32'?'Scripts/python.exe':'bin/python');
  const server=spawn(python,['-m','tests.e2e_server'],{cwd:root,env:{...process.env,CODEPROOF_E2E_PORT:'8011'},windowsHide:true,stdio:['ignore','pipe','pipe']});
  let serverLog='';server.stdout.on('data',d=>serverLog+=d);server.stderr.on('data',d=>serverLog+=d);
  let code;
  try{
    let up=false;
    for(let n=0;n<60;n++){try{up=(await fetch('http://127.0.0.1:8011/health')).ok;}catch{}if(up)break;await wait(250);}
    if(!up)throw Error('Test API did not start: '+serverLog);
    const executable=process.env.CODEPROOF_VSCODE_EXECUTABLE||path.join(process.env.LOCALAPPDATA||'','Programs','Microsoft VS Code','Code.exe');
    const env={...process.env,CODEPROOF_TEST_RUN:run};delete env.ELECTRON_RUN_AS_NODE;
    code=spawn(executable,[workspace,'--new-window','--skip-welcome','--skip-release-notes','--disable-workspace-trust','--disable-extensions','--disable-updates','--disable-gpu',
      '--user-data-dir='+path.join(run,'profile'),'--extensions-dir='+path.join(run,'extensions'),
      '--extensionDevelopmentPath='+(process.env.CODEPROOF_EXTENSION_PATH||path.join(root,'apps/vscode-extension')),'--extensionTestsPath='+path.join(__dirname,'host.cjs')],{env,windowsHide:true,stdio:['ignore','pipe','pipe']});
    let output='';code.stdout.on('data',d=>output+=d);code.stderr.on('data',d=>output+=d);
    const exited=new Promise((resolve,reject)=>{code.on('error',reject);code.on('exit',resolve);});
    const timeout=setTimeout(()=>code.kill(),120000);
    const exitCode=await exited;clearTimeout(timeout);
    await fs.writeFile(path.join(run,'host.log'),output);
    if(exitCode!==0)throw Error('Extension host failed ('+exitCode+'). '+output.slice(-6000));
    const report=JSON.parse(await fs.readFile(path.join(run,'host-results.json'),'utf8'));
    console.log(JSON.stringify({...report,runDirectory:run},null,2));
  }finally{if(code?.exitCode===null)code.kill();server.kill();}
}
main().catch(error=>{console.error(error.message);process.exitCode=1;});
