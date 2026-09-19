param([int]$Port = 11435)
$ErrorActionPreference = 'Stop'
$runtimeDir = Join-Path $env:LOCALAPPDATA 'BeProgram/ollama'
$pidFile = Join-Path $runtimeDir "server-$Port.pid"
if (Test-Path -LiteralPath $pidFile) {
    $ownedProcess = Get-Process -Id ([int](Get-Content -LiteralPath $pidFile)) -ErrorAction SilentlyContinue
    if ($ownedProcess -and $ownedProcess.Path -eq (Join-Path $runtimeDir 'ollama.exe')) {
        Stop-Process -Id $ownedProcess.Id
        Write-Output 'Stopped the BeProgram local model server.'
    }
}
