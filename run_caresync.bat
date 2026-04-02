@echo off
cd /d "%~dp0"
:: Create logs folder to capture errors silently
if not exist logs mkdir logs
:: Use pythonw.exe inside the exact Virtual Environment to HIDE the command prompt window entirely
start "" "%~dp0venv\Scripts\pythonw.exe" "desktop_app.py" 1> "logs\run.log" 2>&1
