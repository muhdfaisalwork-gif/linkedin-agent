@echo off
title NexusAgent - Autonomous LinkedIn Studio Launcher
cls

echo ===================================================================
echo   NEXUSAGENT: AUTONOMOUS LINKEDIN STUDIO LAUNCHER
echo ===================================================================
echo.

cd /d "%~dp0"

REM Find best Python executable
set "PYTHON_EXE="

if exist "%LOCALAPPDATA%\Python\bin\python.exe" (
    set "PYTHON_EXE=%LOCALAPPDATA%\Python\bin\python.exe"
)

if "%PYTHON_EXE%"=="" (
    where py >nul 2>nul
    if %errorlevel% equ 0 set "PYTHON_EXE=py"
)

if "%PYTHON_EXE%"=="" (
    where python >nul 2>nul
    if %errorlevel% equ 0 set "PYTHON_EXE=python"
)

REM Check if uv is available
where uv >nul 2>nul
if %errorlevel% equ 0 (
    echo [OK] Detected 'uv' fast package manager.
    echo Launching NexusAgent...
    uv run run.py
    pause
    exit /b
)

if not "%PYTHON_EXE%"=="" (
    echo [OK] Detected Python: %PYTHON_EXE%
    echo Verifying dependencies...
    "%PYTHON_EXE%" -m pip install -r requirements.txt --quiet
    "%PYTHON_EXE%" run.py
    pause
    exit /b
)

echo [ERROR] Neither 'uv' nor a working Python installation was found.
echo Please install Python 3.10+ from python.org or uv.
pause
