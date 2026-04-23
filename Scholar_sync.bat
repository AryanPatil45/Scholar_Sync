@echo off
cd /d "%~dp0"

echo =========================================
echo       Starting Scholar-Sync Engine       
echo =========================================

echo.
echo [1/3] Starting Python AI Brain (FastAPI)...
start cmd /k ".\venv\Scripts\python.exe -m uvicorn src.api.main:app --reload"

echo [2/3] Starting React Web Interface...
start cmd /k "cd frontend && npm run dev"

echo [3/3] Waiting for engines to warm up...
timeout /t 4 /nobreak > NUL

echo Opening Scholar-Sync in your browser!
start http://localhost:5173

exit