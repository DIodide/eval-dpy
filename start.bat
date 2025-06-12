@echo off
REM Discord Bot Startup Script for Windows
REM This script will create a virtual environment, install dependencies, and start the bot

echo 🤖 Discord Bot Startup Script
echo ==============================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Get Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo 📍 Found Python %PYTHON_VERSION%

REM Check if .env file exists
if not exist ".env" (
    echo ⚠️  .env file not found!
    echo    Please create a .env file with your Discord bot token:
    echo    DISCORD_TOKEN=your_bot_token_here
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist ".venv" (
    echo 📦 Creating virtual environment...
    python -m venv .venv
    echo ✅ Virtual environment created
) else (
    echo 📦 Virtual environment already exists
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call .venv\Scripts\activate.bat

REM Upgrade pip
echo 📈 Upgrading pip...
python -m pip install --upgrade pip >nul 2>&1

REM Install/update requirements
if exist "requirements.txt" (
    echo 📚 Installing/updating dependencies...
    pip install -r requirements.txt
    echo ✅ Dependencies installed
) else (
    echo ❌ requirements.txt not found!
    pause
    exit /b 1
)

REM Check if main.py exists
if not exist "main.py" (
    echo ❌ main.py not found!
    pause
    exit /b 1
)

echo.
echo 🚀 Starting Discord Bot...
echo    Press Ctrl+C to stop the bot
echo ==============================

REM Start the bot
python main.py

pause 