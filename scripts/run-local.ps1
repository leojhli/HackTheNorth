param([switch]$Restart)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath (Split-Path -Parent $PSScriptRoot)
$python = (Resolve-Path '.venv/Scripts/python.exe').Path
$basePython = (& $python -c "import sys; from pathlib import Path; print(Path(sys.base_prefix) / 'python.exe')").Trim()
$listener = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
if ($listener) {
    $running = Get-CimInstance Win32_Process -Filter "ProcessId = $($listener.OwningProcess)"
    $workspaceProcess = $running.ExecutablePath -eq $python
    if ($running.ExecutablePath -eq $basePython) {
        $parent = Get-CimInstance Win32_Process -Filter "ProcessId = $($running.ParentProcessId)"
        $workspaceProcess = $parent.ExecutablePath -eq $python
    }
    if ((-not $workspaceProcess) -or
        ($running.CommandLine -notmatch [regex]::Escape('-m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --no-access-log'))) {
        throw 'Port 8000 belongs to another process. BeProgram did not stop it. Close that process or choose another port before starting.'
    }
    if ($Restart) {
        Stop-Process -Id $listener.OwningProcess
    } else {
        & (Join-Path $PSScriptRoot 'start-local-ai.ps1')
        Write-Output 'BeProgram is already running at http://127.0.0.1:8000. No second backend was started.'
        & $python -m scripts.doctor
        exit $LASTEXITCODE
    }
}
& (Join-Path $PSScriptRoot 'start-local-ai.ps1')
if ($LASTEXITCODE -ne 0) { throw 'Start local AI before running BeProgram.' }
& $python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --no-access-log
