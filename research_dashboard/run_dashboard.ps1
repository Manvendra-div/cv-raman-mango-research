Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

$port = if ($env:RESEARCH_DASHBOARD_PORT) { $env:RESEARCH_DASHBOARD_PORT } else { "8502" }

python -m streamlit run src\research_dashboard\dashboard.py --server.address 127.0.0.1 --server.port $port
