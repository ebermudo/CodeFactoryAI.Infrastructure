$ErrorActionPreference = 'Stop'
$target = Join-Path $PSScriptRoot '../.env'
if (Test-Path -LiteralPath $target) { throw '.env already exists; preserving it.' }
function New-LocalPassword { $bytes = New-Object byte[] 32; $rng = [Security.Cryptography.RandomNumberGenerator]::Create(); try { $rng.GetBytes($bytes); return ([BitConverter]::ToString($bytes)).Replace('-','').ToLowerInvariant() } finally { $rng.Dispose() } }
$content = "POSTGRES_PASSWORD=$(New-LocalPassword)`nRABBITMQ_PASSWORD=$(New-LocalPassword)`nRUNNER_SERVICE_TOKEN=$(New-LocalPassword)`nBRAIN_BOOTSTRAP_PASSWORD=Aa1!$(New-LocalPassword)`n"
[IO.File]::WriteAllText([IO.Path]::GetFullPath($target), $content)
Write-Output 'Local secrets created in ignored .env; never commit it.'
