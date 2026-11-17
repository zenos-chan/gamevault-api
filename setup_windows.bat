@echo off
echo ==============================================
echo Setting up Game Platform API on Windows...
echo ==============================================

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.10+ from python.org and check "Add Python to PATH".
    pause
    exit /b 1
)

:: Create virtual environment if it doesn't exist
if not exist "env\" (
    echo [1/5] Creating virtual environment (env)...
    python -m venv env
) else (
    echo [1/5] Virtual environment already exists.
)

:: Activate virtual environment
echo [2/5] Activating virtual environment...
call env\Scripts\activate.bat

:: Install dependencies
echo [3/5] Installing dependencies from requirements.txt...
pip install -r requirements.txt

:: Apply migrations
echo [4/5] Running database migrations...
python manage.py migrate

:: Seed sample data and superuser
echo [5/5] Seeding sample data and admin account...
python manage.py seed_data

echo ==============================================
echo Setup complete! Starting server...
echo Admin Login: admin / admin123
echo Root API:    http://127.0.0.1:8000/
echo Admin:       http://127.0.0.1:8000/admin/
echo ==============================================
python manage.py runserver
