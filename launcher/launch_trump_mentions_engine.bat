@echo off
setlocal enabledelayedexpansion

echo ============================================
echo   Trump Mentions Engine - One Click Launch
echo ============================================

cd /d "%~dp0"

set "PY_CMD="
where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    py -3.11 -c "import sys; print(sys.version_info[:2])" >nul 2>nul
    if %ERRORLEVEL% EQU 0 (
        set "PY_CMD=py -3.11"
    ) else (
        set "PY_CMD=py"
    )
)

if "%PY_CMD%"=="" (
    where python >nul 2>nul
    if %ERRORLEVEL% EQU 0 (
        set "PY_CMD=python"
    )
)

if "%PY_CMD%"=="" (
    echo [ERROR] Python not found. Install Python 3.11+ and retry.
    pause
    exit /b 1
)

echo [INFO] Using Python command: %PY_CMD%

if not exist ".venv\Scripts\python.exe" (
    echo [INFO] Creating virtual environment...
    %PY_CMD% -m venv .venv
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
)

call ".venv\Scripts\activate.bat"
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to activate virtual environment.
    pause
    exit /b 1
)

echo [INFO] Upgrading pip...
python -m pip install --upgrade pip
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed while upgrading pip.
    pause
    exit /b 1
)

echo [INFO] Installing dependencies...
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Dependency installation failed.
    pause
    exit /b 1
)

if not exist data mkdir data
if not exist logs mkdir logs

echo [INFO] Launching Trump Mentions Engine...
python -m app.main
set EXIT_CODE=%ERRORLEVEL%

if %EXIT_CODE% NEQ 0 (
    echo [ERROR] Application exited with code %EXIT_CODE%.
    pause
)

exit /b %EXIT_CODE%
