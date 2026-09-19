param([int]$Port = 11435)
$ErrorActionPreference = 'Stop'
if ($Port -lt 1024 -or $Port -gt 65535) { throw 'Choose a local port between 1024 and 65535.' }
$runtimeDir = Join-Path $env:LOCALAPPDATA 'CodeProof/ollama'
$executable = Join-Path $runtimeDir 'ollama.exe'
if (-not (Test-Path -LiteralPath $executable)) { throw 'Run ./scripts/setup-local-ai.ps1 first.' }
$pidFile = Join-Path $runtimeDir "server-$Port.pid"
$listener = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
if ($listener) {
    $ownedId = if (Test-Path -LiteralPath $pidFile) { [int](Get-Content -LiteralPath $pidFile) } else { 0 }
    $existing = Get-Process -Id $ownedId -ErrorAction SilentlyContinue
    if (-not $existing -or $existing.Path -ne $executable -or $listener.OwningProcess -notcontains $ownedId) {
        throw "Port $Port belongs to another process. CodeProof will not reuse an unverified Ollama server."
    }
    Write-Output "CodeProof local AI is already running on 127.0.0.1:$Port."
    exit 0
}
$env:OLLAMA_HOST = "127.0.0.1:$Port"
$env:OLLAMA_NO_CLOUD = '1'
$env:OLLAMA_MODELS = Join-Path $runtimeDir 'models'
$env:OLLAMA_NUM_PARALLEL = '1'
$env:OLLAMA_MAX_LOADED_MODELS = '1'
$env:OLLAMA_MAX_QUEUE = '2'
$env:OLLAMA_CONTEXT_LENGTH = '16384'
$env:OLLAMA_FLASH_ATTENTION = '1'
$env:OLLAMA_KV_CACHE_TYPE = 'q8_0'
$process = Start-Process -FilePath $executable -ArgumentList 'serve' -WindowStyle Hidden -PassThru -WorkingDirectory $runtimeDir -RedirectStandardOutput (Join-Path $runtimeDir 'server.stdout.log') -RedirectStandardError (Join-Path $runtimeDir 'server.stderr.log')
$process.Id | Set-Content -LiteralPath $pidFile
for ($attempt = 0; $attempt -lt 30; $attempt++) {
    try {
        $null = Invoke-RestMethod "http://127.0.0.1:$Port/api/version" -TimeoutSec 2
        Write-Output "Local AI started on 127.0.0.1:$Port with cloud features disabled."
        exit 0
    } catch { Start-Sleep -Milliseconds 500 }
}
throw "Ollama did not start. Inspect $runtimeDir/server.stderr.log."
