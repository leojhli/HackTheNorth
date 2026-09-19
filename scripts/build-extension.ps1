$ErrorActionPreference = 'Stop'
$workspaceRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $workspaceRoot
$localNode = Get-ChildItem -LiteralPath '.tools/node' -Directory -ErrorAction SilentlyContinue | Select-Object -First 1
if ($localNode) { $env:PATH = $localNode.FullName + ';' + $env:PATH }
& npm.cmd --prefix apps/vscode-extension run build
if ($LASTEXITCODE -ne 0) { throw 'Sidebar build failed.' }
