@echo off
chcp 65001 >nul
echo ========================================
echo   Umax CRM - demo-dannye
echo ========================================

call "%~dp02_start_postgres.bat"
if errorlevel 1 exit /b 1

call "%~dp0_common.bat"
python -m scripts seed
if errorlevel 1 (
    pause
    exit /b 1
)

echo.
echo [OK] Demo-dannye zagruzheny
echo     admin / admin123
pause
