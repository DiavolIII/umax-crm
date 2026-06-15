4@echo off
chcp 65001 >nul
echo ========================================
echo   Umax CRM - ostanovka servera
echo ========================================

set "KILLED="
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000" ^| findstr "LISTENING"') do (
    echo [+] Ostanovka processa PID %%a...
    taskkill /F /PID %%a >nul 2>&1
    set "KILLED=1"
)

if defined KILLED (
    echo [OK] Server ostanovlen
    timeout /t 1 /nobreak >nul
) else (
    echo [i] Server na portu 8000 ne zapuschen
)

exit /b 0
