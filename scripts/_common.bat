@echo off
chcp 65001 >nul
set "BACKEND=%~dp0..\backend"
cd /d "%BACKEND%"

if not exist .env copy /Y .env.example .env >nul

if not exist venv (
    python -m venv venv
)

call venv\Scripts\activate.bat
set PYTHONIOENCODING=utf-8

python -m ensurepip --upgrade >nul 2>&1