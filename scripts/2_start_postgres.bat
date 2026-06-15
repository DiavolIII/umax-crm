@echo off
chcp 65001 >nul
echo ========================================
echo   Umax CRM - zapusk PostgreSQL
echo ========================================

set "FOUND="
for %%S in (
    postgresql-x64-17
    postgresql-x64-16
    postgresql-x64-15
    postgresql-x64-14
    postgresql-x64-13
    postgresql-x64-12
    postgresql-x64-11
    postgresql-x64-10
    postgresql
) do (
    if not defined FOUND (
        sc query "%%S" >nul 2>&1
        if not errorlevel 1 set "FOUND=%%S"
    )
)

if not defined FOUND (
    echo [!] Sluzhba PostgreSQL ne naidena
    echo     Ustanovite s https://www.postgresql.org/download/
    pause
    exit /b 1
)

echo [+] Sluzhba: %FOUND%

sc query "%FOUND%" | find "RUNNING" >nul
if errorlevel 1 (
    echo [+] Zapusk...
    net start "%FOUND%"
    if errorlevel 1 (
        echo [!] Zapustite ot imeni administratora
        pause
        exit /b 1
    )
    timeout /t 2 /nobreak >nul
) else (
    echo [OK] Uzhe zapuschen
)

call "%~dp0_common.bat"
python -m scripts check
if errorlevel 1 (
    echo [!] Prover'te DB_PASSWORD= 1111 v backend\.env
    pause
    exit /b 1
)

echo [OK] Podklyuchenie uspeshno
exit /b 0
