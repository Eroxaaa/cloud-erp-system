@echo off
setlocal

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment...
    python -m venv .venv
)

echo Installing requirements...
".venv\Scripts\python.exe" -m pip install -r requirements.txt

echo.
echo Starting Wholesale ERP app...
echo Open: http://localhost:8000/login.html
echo Login: admin / admin123
echo.

".venv\Scripts\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port 8000
