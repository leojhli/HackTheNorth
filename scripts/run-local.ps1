$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath (Split-Path -Parent $PSScriptRoot)
& (Join-Path $PSScriptRoot 'start-local-ai.ps1')
if ($LASTEXITCODE -ne 0) { throw 'Start local AI before running BeProgram.' }
& '.venv/Scripts/python.exe' -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --no-access-log
