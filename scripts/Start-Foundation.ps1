param([ValidateSet('docker','host')][string]$Mode = 'docker')
$ErrorActionPreference = 'Stop'
python (Join-Path $PSScriptRoot 'environment.py') up --mode $Mode
if ($LASTEXITCODE -ne 0) { throw 'Development environment failed startup. Run environment.py logs.' }
