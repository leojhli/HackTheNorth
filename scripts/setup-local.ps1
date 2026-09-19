$ErrorActionPreference = 'Stop'
$workspaceRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $workspaceRoot
$pythonCommand = if (Test-Path '.venv/Scripts/python.exe') { '.venv/Scripts/python.exe' } else { 'python' }
if (-not (Test-Path '.venv')) { & $pythonCommand -m venv .venv }
$localUv = Join-Path $workspaceRoot '.tools/uv/uv.exe'
if (Test-Path $localUv) {
    $env:UV_CACHE_DIR = Join-Path $workspaceRoot '.tools/uv-cache'
    & $localUv pip install --python '.venv/Scripts/python.exe' -r backend/requirements.lock.txt
} else { & '.venv/Scripts/python.exe' -m pip install -r backend/requirements.lock.txt }
if ($LASTEXITCODE -ne 0) { throw 'Backend dependency install failed.' }
if (-not (Test-Path '.env')) {
    & '.venv/Scripts/python.exe' -c "from pathlib import Path; import secrets; p=Path('.env.example').read_text(); p=p.replace('AUTH_MODE=supabase','AUTH_MODE=local',1).replace('LOCAL_DEV_TOKEN=','LOCAL_DEV_TOKEN='+secrets.token_urlsafe(32),1); Path('.env').write_text(p)"
    Write-Output 'Created ignored .env with a local-only token. No provider API keys are required.'
}
& '.venv/Scripts/python.exe' -m backend.migrate
if ($LASTEXITCODE -ne 0) { throw 'Database migration failed. Check .env before continuing.' }
$localNode = Get-ChildItem -LiteralPath '.tools/node' -Directory -ErrorAction SilentlyContinue | Select-Object -First 1
if ($localNode) { $env:PATH = $localNode.FullName + ';' + $env:PATH }
$env:npm_config_cache = Join-Path $workspaceRoot '.tools/npm-cache'
Push-Location -LiteralPath 'apps/dashboard'
try { npm.cmd ci --offline=false --no-audit --no-fund; if ($LASTEXITCODE -ne 0) { throw 'Frontend dependency install failed.' }; npm.cmd run build; if ($LASTEXITCODE -ne 0) { throw 'Frontend build failed.' } } finally { Pop-Location }
Write-Output 'Start: .venv/Scripts/python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --no-access-log'
& npm.cmd --prefix apps/dashboard run build:extension
if ($LASTEXITCODE -ne 0) { throw 'VS Code sidebar build failed.' }
& (Join-Path $PSScriptRoot 'setup-local-ai.ps1')
if ($LASTEXITCODE -ne 0) { throw 'Local model setup failed.' }
