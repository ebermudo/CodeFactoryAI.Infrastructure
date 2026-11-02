$ErrorActionPreference = 'Stop'
docker compose --env-file (Join-Path $PSScriptRoot '../.env') -f (Join-Path $PSScriptRoot '../compose.yaml') stop
if ($LASTEXITCODE -ne 0) { throw 'Could not stop foundation dependencies.' }
