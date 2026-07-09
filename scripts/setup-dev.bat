@echo off
REM Development startup script for local setup (Windows)

setlocal enabledelayedexpansion

echo.
echo 🚀 Enterprise Purple Team Platform - Development Setup
echo ============================================
echo.

REM Check Python version
echo 📦 Checking Python version...
python --version >nul 2>&1 || (
    echo ❌ Python is required. Please install Python 3.12+
    exit /b 1
)

REM Create venv if it doesn't exist
if not exist "backend\venv" (
    echo 📦 Creating Python virtual environment...
    python -m venv backend\venv
)

REM Activate venv
echo 📦 Activating virtual environment...
call backend\venv\Scripts\activate.bat

REM Install dependencies
echo 📦 Installing Python dependencies...
python -m pip install --upgrade pip
pip install -r backend\requirements.txt

REM Check PostgreSQL
echo 🗄️  Checking PostgreSQL...
psql -U admin -d postgres -c "SELECT 1;" >nul 2>&1 || (
    echo ⚠️  PostgreSQL not running. Start it using Docker or locally.
)

REM Check Redis
echo 📡 Checking Redis...
redis-cli ping >nul 2>&1 || (
    echo ⚠️  Redis not running. Start it using Docker or locally.
)

REM Seed data
echo 🌱 Seeding initial data...
python backend\scripts\seed_data.py

echo.
echo ✅ Setup complete!
echo.
echo 🚀 To start the server, run:
echo    cd backend
echo    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
echo.
echo 📖 API Documentation:
echo    http://localhost:8000/docs
echo.
echo 🔑 Test Credentials:
echo    Username: admin
echo    Password: AdminPassword123
echo.

endlocal
