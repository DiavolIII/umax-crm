@echo off
chcp 65001 >nul
echo ========================================
echo   Umax CRM - polnyj zapusk
echo ========================================
echo.

call "%~dp01_install.bat" auto
if errorlevel 1 exit /b 1

call "%~dp02_start_postgres.bat"
if errorlevel 1 exit /b 1

call "%~dp06_stop_server.bat"

call "%~dp0_common.bat"
python -m scripts init
if errorlevel 1 (
    pause
    exit /b 1
)

call "%~dp05_run_server.bat"
