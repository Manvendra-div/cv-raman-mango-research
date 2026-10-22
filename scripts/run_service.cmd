@echo off
REM ============================================================================
REM  Helper (Windows) - start ONE service inside the current console window.
REM
REM    run_service.cmd api [host] [port] [simple]
REM    run_service.cmd ui  [ui_port] [api_port] [simple]
REM
REM  Called by ..\start.bat. Output is written to logs\*.log
REM ============================================================================
setlocal enabledelayedexpansion

set "SERVICE=%~1"
set "ARG2=%~2"
set "ARG3=%~3"
set "ARG4=%~4"

cd /d "%~dp0\.."

set "PY=%~dp0..\.venv\Scripts\python.exe"
if not exist "!PY!" set "PY=python"

if not exist "logs" mkdir "logs"

if /I "!SERVICE!"=="api" (
    if not defined ARG2 set "ARG2=127.0.0.1"
    if not defined ARG3 set "ARG3=8000"
    echo [API] http://!ARG2!:!ARG3!   ^(log: logs\api.log^)
    "!PY!" -m uvicorn backend.app.main:app --host !ARG2! --port !ARG3! > logs\api.log 2>&1
    goto :eof
)

if /I "!SERVICE!"=="ui" (
    if not defined ARG2 set "ARG2=8501"
    if not defined ARG3 set "ARG3=8000"
    set "DSS_API_URL=http://127.0.0.1:!ARG3!"
    set "APP=src\dss\dashboard.py"
    if /I "!ARG4!"=="simple" set "APP=frontend\app.py"
    echo [UI] http://127.0.0.1:!ARG2!  app=!APP!  ^(log: logs\frontend.log^)
    "!PY!" -m streamlit run "!APP!" --server.port !ARG2! --server.address 127.0.0.1 > logs\frontend.log 2>&1
    goto :eof
)

echo Unknown service "!SERVICE!". Use: api ^| ui
exit /b 1
