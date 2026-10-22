@echo off
REM ============================================================================
REM  Zone-Aware Mango Soil Intelligence and Yield Gap DSS
REM  Start script for Windows
REM
REM    start.bat                   -> install if needed, start API + dashboard
REM    start.bat --install         -> force (re)install dependencies
REM    start.bat --tests           -> run pytest before starting
REM    start.bat --backend-only    -> API only
REM    start.bat --frontend-only   -> dashboard only
REM    start.bat --simple-frontend -> minimal frontend\app.py
REM    start.bat --api-port 9000 --ui-port 8601
REM ============================================================================
setlocal enabledelayedexpansion

cd /d "%~dp0"

set "API_PORT=8000"
set "UI_PORT=8501"
set "API_HOST=127.0.0.1"
set "DO_INSTALL=0"
set "DO_TESTS=0"
set "RUN_BACKEND=1"
set "RUN_FRONTEND=1"
set "SIMPLE_FRONTEND=0"

REM ---------------------------------------------------------------- parse args
:parse
if "%~1"=="" goto afterparse
if /I "%~1"=="--install"         goto opt_install
if /I "%~1"=="--tests"           goto opt_tests
if /I "%~1"=="--backend-only"    goto opt_backend
if /I "%~1"=="--frontend-only"   goto opt_frontend
if /I "%~1"=="--simple-frontend" goto opt_simple
if /I "%~1"=="--api-port"        goto opt_apiport
if /I "%~1"=="--ui-port"         goto opt_uiport
if /I "%~1"=="--help"            goto usage
if /I "%~1"=="-h"                goto usage
echo Unknown option: %~1
goto usage

:opt_install
set "DO_INSTALL=1"
shift
goto parse
:opt_tests
set "DO_TESTS=1"
shift
goto parse
:opt_backend
set "RUN_FRONTEND=0"
shift
goto parse
:opt_frontend
set "RUN_BACKEND=0"
shift
goto parse
:opt_simple
set "SIMPLE_FRONTEND=1"
shift
goto parse
:opt_apiport
set "API_PORT=%~2"
shift
shift
goto parse
:opt_uiport
set "UI_PORT=%~2"
shift
shift
goto parse
:afterparse

REM ------------------------------------------------------------ python runtime
echo ==^> Python lookup
set "LAUNCHER="
set "LAUNCHER_ARGS="
if exist "%~dp0.venv\Scripts\python.exe" (
    set "PY=%~dp0.venv\Scripts\python.exe"
    set "LAUNCHER_ARGS="
    goto have_py
)
where python >nul 2>nul && set "LAUNCHER=python"
if not defined LAUNCHER (
    where py >nul 2>nul && (
        set "LAUNCHER=py"
        set "LAUNCHER_ARGS=-3"
    )
)
if not defined LAUNCHER (
    echo [x] Python not found. Install Python 3.11+ and add it to PATH.
    exit /b 1
)
set "PY=%LAUNCHER%"

:have_py
for /f "tokens=*" %%v in ('"%PY%" %LAUNCHER_ARGS% --version 2^>^&1') do set "PYVER=%%v"
echo ==^> Python: %PY% %LAUNCHER_ARGS% (%PYVER%)

if not exist "%~dp0.venv\Scripts\python.exe" (
    echo ==^> Creating virtual environment .venv
    "%PY%" %LAUNCHER_ARGS% -m venv "%~dp0.venv"
    if errorlevel 1 (
        echo [x] venv creation failed
        exit /b 1
    )
    set "PY=%~dp0.venv\Scripts\python.exe"
)

REM --------------------------------------------------------------- dependencies
echo ==^> Checking dependencies
"%PY%" -c "import fastapi, uvicorn, streamlit, pandas, sklearn" >nul 2>nul
if errorlevel 1 set "DO_INSTALL=1"
if "%DO_INSTALL%"=="1" (
    echo ==^> Installing dependencies from requirements.txt - this can take a few minutes
    "%PY%" -m pip install --upgrade pip --quiet
    "%PY%" -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [x] Dependency install failed
        exit /b 1
    )
) else (
    echo ==^> Dependencies already installed ^(use --install to force reinstall^)
)

if "%DO_TESTS%"=="1" (
    echo ==^> Running tests
    "%PY%" -m pytest -q
)

if not exist "%~dp0logs" mkdir "%~dp0logs"

REM -------------------------------------------------------------------- backend
if "%RUN_BACKEND%"=="1" (
    echo ==^> Starting API on http://%API_HOST%:%API_PORT%   log: logs\api.log
    start "Mango DSS API" cmd /k call "%~dp0scripts\run_service.cmd" api %API_HOST% %API_PORT%
    where curl >nul 2>nul
    if not errorlevel 1 call :wait_for_api
    echo ==^> API window opened - see logs\api.log
)

REM ------------------------------------------------------------------- frontend
if "%RUN_FRONTEND%"=="1" (
    if "%SIMPLE_FRONTEND%"=="1" (
        set "SIMPLE_ARG=simple"
    ) else (
        set "SIMPLE_ARG=full"
    )
    echo ==^> Starting dashboard on http://127.0.0.1:%UI_PORT%
    start "Mango DSS Dashboard" cmd /k call "%~dp0scripts\run_service.cmd" ui %UI_PORT% %API_PORT% !SIMPLE_ARG!
)

echo.
echo ==^> Ready.
if "%RUN_BACKEND%"=="1"  echo     API      : http://%API_HOST%:%API_PORT%   ^(docs: /docs^)
if "%RUN_FRONTEND%"=="1" echo     Dashboard: http://127.0.0.1:%UI_PORT%
echo     Logs     : logs\api.log , logs\frontend.log
echo     Stop     : close the two console windows
echo.
exit /b 0

REM --------------------------------------------------- wait for API /health
:wait_for_api
set /a WAITED=0
:wait_loop
if !WAITED! GEQ 40 goto wait_done
curl -fsS "http://%API_HOST%:%API_PORT%/health" >nul 2>nul
if not errorlevel 1 goto wait_done
ping -n 2 127.0.0.1 >nul
set /a WAITED+=1
goto wait_loop
:wait_done
exit /b 0

:usage
echo.
echo Usage: start.bat [--install] [--tests] [--backend-only] [--frontend-only]
echo                  [--simple-frontend] [--api-port N] [--ui-port N]
echo.
echo   --install         reinstall dependencies from requirements.txt
echo   --tests           run pytest before starting
echo   --backend-only    start only the API
echo   --frontend-only   start only the dashboard
echo   --simple-frontend use frontend\app.py instead of the full dashboard
echo   --api-port N      API port ^(default 8000^)
echo   --ui-port N       dashboard port ^(default 8501^)
echo.
exit /b 0
