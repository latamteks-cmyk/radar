@echo off
REM Project setup script for Radar Trading Intelligence Platform
REM Run this script to initialize the project for the first time

echo =====================================
echo Radar Trading Platform - Setup
echo =====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/7] Python found!
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo [2/7] Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
) else (
    echo [2/7] Virtual environment already exists
)
echo.

REM Activate virtual environment
echo [3/7] Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Install dependencies
echo [4/7] Installing dependencies...
pip install -e ".[dev]"
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo.

REM Copy .env.example to .env if .env doesn't exist
if not exist ".env" (
    echo [5/7] Creating .env file from template...
    copy .env.example .env
    echo.
    echo WARNING: Please edit .env file with your configuration
    echo.
) else (
    echo [5/7] .env file already exists
)
echo.

REM Create necessary directories
echo [6/7] Creating runtime directories...
if not exist "logs\" mkdir logs
if not exist "notebooks\analysis" mkdir notebooks\analysis
if not exist "notebooks\experiments" mkdir notebooks\experiments
echo.

REM Initialize database (if PostgreSQL is available)
echo [7/7] Database setup instructions:
echo.
echo To setup the database:
echo   1. Ensure PostgreSQL is running
echo   2. Create database: createdb radar_trading
echo   3. Run migrations: alembic upgrade head
echo.

echo =====================================
echo Setup complete!
echo =====================================
echo.
echo Next steps:
echo   1. Edit .env with your configuration
echo   2. Setup PostgreSQL database
echo   3. Run: alembic upgrade head
echo   4. Start backend: uvicorn src.main:app --reload
echo   5. Start frontend: cd src\presentation\web ^&^& npm run dev
echo.
pause
