@echo off
title CFCS v2.0 — Criminal Face Detection System
color 0B
cls

echo.
echo  ╔══════════════════════════════════════════════════════╗
echo  ║   CFCS v2.0 — Criminal Face Detection System        ║
echo  ║   AI-Powered Smart Surveillance Platform             ║
echo  ╚══════════════════════════════════════════════════════╝
echo.

:: Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    echo  [*] Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo  [!] No venv found — using system Python
)

:: Seed the database (idempotent — safe to run every time)
echo  [*] Initializing database...
python seed_db.py

echo.
echo  [*] Starting CFCS server...
echo  [*] Open your browser at: http://localhost:8000
echo  [*] Login: admin / admin123
echo  [*] Press Ctrl+C to stop
echo.

:: Start FastAPI server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

pause
