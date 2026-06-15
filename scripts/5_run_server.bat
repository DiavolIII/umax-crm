@echo off
chcp 65001 >nul
echo ========================================
echo   Umax CRM - server
echo ========================================

call "%~dp02_start_postgres.bat"
if errorlevel 1 exit /b 1

call "%~dp06_stop_server.bat"

call "%~dp0_common.bat"

echo.
echo   http://localhost:8000
echo   Login: admin / admin123
echo   Ctrl+C - ostanovit
echo.

python -m app
