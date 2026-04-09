@echo off
echo ==========================================
echo CareSync Mega-Overhaul Deployment Script
echo ==========================================
echo.
echo 1. Pushing updates to GitHub (Render will auto-deploy)...
git add .
git commit -m "Mega Overhaul Features Deployed (AJAX, Universal Search, Leaves)"
git push
echo Git Push Complete!
echo.
echo 2. Re-building Desktop Executable (PyInstaller)...
call .\venv\Scripts\activate.bat
pyinstaller --noconfirm --onedir --windowed --add-data "templates;templates" --add-data "static;static" app.py
echo.
echo Build Complete!
echo.
echo All Done! You can now close this window.
pause
