$ErrorActionPreference = "Stop"
Set-Location (Resolve-Path "$PSScriptRoot\..")
$env:PYTHONPATH = (Get-Location).Path
python -m uvicorn src.dss.api:app --host 127.0.0.1 --port 8000

