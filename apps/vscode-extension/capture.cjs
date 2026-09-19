const {execFile} = require('node:child_process');
const {promisify} = require('node:util');
const fs = require('node:fs/promises');
const path = require('node:path');
const crypto = require('node:crypto');
const run = promisify(execFile);
function within(root,target) {
  const relative=path.relative(root,target);
  return relative!=='' && relative!=='..' && !relative.startsWith('..'+path.sep) && !path.isAbsolute(relative);
}

async function git(root, ...args) {
  const result = await run('git', ['-C', root, ...args], {encoding:'utf8', maxBuffer:2_000_000, windowsHide:true});
  return result.stdout;
}

async function collect(root, project) {
  root=await fs.realpath(root);
  if ([...project.scope, ...project.exclusions].some(rule => /[*?[\]]/.test(rule)))
    throw Error('The VS Code capture companion requires literal file/directory scope. Update glob rules in Project settings.');
  const hasHead = await git(root, 'rev-parse', '--verify', 'HEAD').then(() => true, () => false);
  const tracked = hasHead ? await git(root, 'diff', 'HEAD', '--name-only', '-z') : await git(root, 'ls-files', '--cached', '-z');
  const untracked = await git(root, 'ls-files', '--others', '--exclude-standard', '-z');
  const files = [];
  for (const file of [...new Set((tracked+'\0'+untracked).split('\0').filter(Boolean))].sort()) {
    if (!/\.(?:tsx?|jsx?|mjs|cjs)$/.test(file) || /(^|\/)(?:\.env[^/]*|node_modules|dist|build|coverage|vendor|\.git|\.venv|\.tools|\.next|__pycache__)(\/|$)|\.(?:min\.js|d\.ts|generated\.ts)$/.test(file)) continue;
    const matches = p => p==='.' || file===p.replace(/\/$/,'') || file.startsWith(p.replace(/\/$/,'')+'/');
    if (!project.scope.some(matches) || project.exclusions.some(matches)) continue;
    const ignored = await run('git',['-C',root,'check-ignore','--no-index','-q','--',file],{windowsHide:true}).then(()=>true,()=>false);
    if (ignored) continue;
    const local = path.resolve(root,file);
    if (!within(root,local)) throw Error('Capture path left repository.');
    const stat = await fs.lstat(local).catch(error => { if(error.code==='ENOENT')return null; throw error; });
    if (stat?.isSymbolicLink() || stat?.size>100000) throw Error('Excluded oversized or symlink source; narrow scope.');
    if (stat && !within(root,await fs.realpath(local))) throw Error('Source resolves outside repository.');
    const before = hasHead ? await git(root,'show','HEAD:'+file).catch(()=> '') : '';
    const after = stat ? await fs.readFile(local,'utf8') : '';
    if (before===after) continue;
    if (Buffer.byteLength(before)>100000) throw Error('The previous source exceeds capture bounds. Narrow scope.');
    if (/\x00|-----BEGIN [A-Z ]*PRIVATE KEY-----|\b(?:sk-(?:proj-)?[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{20,}|AKIA[A-Z0-9]{16})|(?:api[_-]?key|password|secret|token)\s*[:=]\s*["'][^"'\s]{8,}/i.test(before+after))
      throw Error('Potential secret or binary in approved source. Exclude the file before upload.');
    files.push({path:file.replace(/\\/g,'/'),before,after});
  }
  if (files.length>30) throw Error('Narrow scope to at most 30 changed files.');
  return {files,provenance:'user_reported_manual',idempotency_key:crypto.createHash('sha256').update(JSON.stringify(files)).digest('hex')};
}
module.exports = {collect,git,within};
