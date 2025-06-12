@echo off
REM Discord Bot Startup Script for Windows
REM This script will set up the environment and start the Discord bot

echo 🤖 Discord Bot Startup Script
echo ==============================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python %PYTHON_VERSION% found

REM Check if .env file exists
if not exist ".env" (
    echo ❌ .env file not found!
    echo Please create a .env file with your Discord token:
    echo   DISCORD_TOKEN=your_bot_token_here
    echo.
    echo Optional database configuration:
    echo   DATABASE_HOST=your_host
    echo   DATABASE_PORT=5432
    echo   DATABASE_NAME=your_database
    echo   DATABASE_USER=your_user
    echo   DATABASE_PASSWORD=your_password
    pause
    exit /b 1
)

echo ✅ .env file found

REM Create virtual environment if it doesn't exist
if not exist ".venv" (
    echo 📦 Creating virtual environment...
    python -m venv .venv
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment found
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Upgrade pip
echo 📦 Upgrading pip...
python -m pip install --upgrade pip

REM Install/upgrade requirements
if exist "requirements.txt" (
    echo 📦 Installing/updating dependencies...
    pip install -r requirements.txt
    echo ✅ Dependencies installed
) else (
    echo ❌ requirements.txt not found!
    pause
    exit /b 1
)

REM Start the bot
echo.
echo 🚀 Starting Discord bot...
echo Note: Environment variables will be validated automatically before startup
echo Press Ctrl+C to stop the bot
echo.

python main.py
pause 