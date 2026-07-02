@echo off
echo ===================================================
echo Criminal Face Recognition System (CFCS)
echo ===================================================
echo.
echo Seeding database with default admin user if not exists...
call venv\Scripts\python.exe seed_db.py
echo.
echo Starting the web server...
echo Access the application at: http://localhost:8000
echo.
call venv\Scripts\uvicorn.exe main:app --host 0.0.0.0 --port 8000
pause
