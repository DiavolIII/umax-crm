@echo off
echo ========================================
echo   Umax CRM - ustanovka zavisimostej
echo ========================================
call "%~dp0_common.bat"

if not exist venv\Scripts\python.exe (
    echo [+] Sozdanie venv...
    python -m venv venv
)

call venv\Scripts\activate.bat
python -m ensurepip --upgrade >nul 2>&1

echo [+] Obnovlenie pip...
python -m pip install --upgrade pip -q

echo [+] Ustanovka paketov...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo [!] Oshibka ustanovki
    pause
    exit /b 1
)

echo.
echo [OK] Zavisimosti ustanovleny
if /i not "%~1"=="auto" pause
