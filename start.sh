#!/bin/bash

# Discord Bot Startup Script for Unix/Linux/macOS
# This script will set up the environment and start the Discord bot

set -e  # Exit on any error

echo "🤖 Discord Bot Startup Script"
echo "=============================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8+ and try again"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python $PYTHON_VERSION found"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "Please create a .env file with your Discord token:"
    echo "  DISCORD_TOKEN=your_bot_token_here"
    echo ""
    echo "Optional database configuration:"
    echo "  DATABASE_HOST=your_host"
    echo "  DATABASE_PORT=5432"
    echo "  DATABASE_NAME=your_database"
    echo "  DATABASE_USER=your_user" 
    echo "  DATABASE_PASSWORD=your_password"
    exit 1
fi

echo "✅ .env file found"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment found"
fi

# Activate virtual environment
source .venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
python -m pip install --upgrade pip

# Install/upgrade requirements
if [ -f "requirements.txt" ]; then
    echo "📦 Installing/updating dependencies..."
    pip install -r requirements.txt
    echo "✅ Dependencies installed"
else
    echo "❌ requirements.txt not found!"
    exit 1
fi

# Check if main.py exists
if [ ! -f "main.py" ]; then
    echo "❌ main.py not found!"
    exit 1
fi

# Start the bot
echo ""
echo "🚀 Starting Discord bot..."
echo "Note: Environment variables will be validated automatically before startup"
echo "Press Ctrl+C to stop the bot"
echo ""

python main.py 