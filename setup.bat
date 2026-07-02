@echo off
echo ===================================================
echo Criminal Face Recognition System (CFCS) - Setup
echo ===================================================
echo.
echo 1. Creating Virtual Environment...
python -m venv venv

echo.
echo 2. Installing Requirements...
call venv\Scripts\python.exe -m pip install --upgrade pip
call venv\Scripts\python.exe -m pip install fastapi uvicorn sqlalchemy passlib[bcrypt] python-multipart jinja2 aiofiles opencv-contrib-python numpy python-jose

echo.
echo 3. Initializing Database and Admin User...
call venv\Scripts\python.exe seed_db.py

echo.
echo ===================================================
echo Setup Complete! You can now start the application.
echo Please run 'run.bat' to launch the system.
echo ===================================================
pause
