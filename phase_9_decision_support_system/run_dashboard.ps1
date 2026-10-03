$ErrorActionPreference = "Stop"
Set-Location (Resolve-Path "$PSScriptRoot\..")
$env:PYTHONPATH = (Get-Location).Path
$env:DSS_API_URL = "http://127.0.0.1:8000"
streamlit run src\dss\dashboard.py --server.address 127.0.0.1 --server.port 8501

