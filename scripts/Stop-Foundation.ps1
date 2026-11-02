$ErrorActionPreference = 'Stop'
python (Join-Path $PSScriptRoot 'environment.py') stop
if ($LASTEXITCODE -ne 0) { throw 'Could not stop development environment.' }
