param([ValidateSet('qwen2.5-coder:7b','qwen2.5-coder:3b')][string]$Model = 'qwen2.5-coder:7b')
$ErrorActionPreference = 'Stop'
$runtimeDir = Join-Path $env:LOCALAPPDATA 'CodeProof/ollama'
New-Item -ItemType Directory -Force -Path $runtimeDir | Out-Null
$archive = Join-Path $runtimeDir 'ollama-windows-amd64.zip'
$executable = Join-Path $runtimeDir 'ollama.exe'
# Pinned official portable distribution; no installer, account or system PATH change.
$version = 'v0.34.2'
$sha256 = '8f3fd071a2a2f9497b562f43502c77c2b701a99d1ee5dfda28da8c786373063b'
if (-not (Test-Path -LiteralPath $executable)) {
    if (-not (Test-Path -LiteralPath $archive)) {
        Write-Output 'Downloading Ollama (about 1.5 GB). No account or payment is required.'
        & curl.exe --fail --location --silent --show-error --retry 2 --output $archive "https://github.com/ollama/ollama/releases/download/$version/ollama-windows-amd64.zip"
        if ($LASTEXITCODE -ne 0) { throw 'Ollama download failed. Remove the incomplete ZIP and retry.' }
    }
    if ((Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash -ne $sha256) { throw 'Ollama ZIP checksum mismatch. Remove this ZIP and retry.' }
    Expand-Archive -LiteralPath $archive -DestinationPath $runtimeDir -Force
}
& (Join-Path $PSScriptRoot 'start-local-ai.ps1')
if ($LASTEXITCODE -ne 0) { throw 'Could not start local AI.' }
$env:OLLAMA_HOST = '127.0.0.1:11435'
$env:OLLAMA_NO_CLOUD = '1'
Write-Output "Downloading local $Model weights (7B: about 4.7 GB; 3B: about 1.9 GB). No inference credits are used."
& $executable pull $Model
if ($LASTEXITCODE -ne 0) { throw 'Model download failed. Rerun this script to resume.' }
Write-Output "Ready. Set OLLAMA_MODEL=$Model in .env. Start CodeProof with ./scripts/run-local.ps1."
