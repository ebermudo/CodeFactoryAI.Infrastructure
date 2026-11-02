$ErrorActionPreference = 'Stop'
$compose = Join-Path $PSScriptRoot '../compose.yaml'
$envFile = Join-Path $PSScriptRoot '../.env'
if (!(Test-Path $envFile)) { throw 'Run Initialize-Local.ps1 first.' }
docker compose --env-file $envFile -f $compose up -d --wait --wait-timeout 180
if ($LASTEXITCODE -ne 0) { throw 'Foundation dependencies failed readiness.' }
