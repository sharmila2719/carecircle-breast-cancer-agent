@echo off
REM CareCircle Setup Script for Windows
echo.
echo ====================================
echo   CareCircle - Setup Script
echo   Breast Cancer Screening Agent
echo ====================================
echo.

REM Check Python version
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)

echo [1/5] Creating virtual environment...
python -m venv venv
call venv\Scripts\activate

echo [2/5] Upgrading pip...
python -m pip install --upgrade pip

echo [3/5] Installing dependencies...
pip install -r requirements.txt

echo [4/5] Setting up environment file...
if not exist .env (
    copy .env.example .env
    echo Created .env file - please update with your AWS credentials
) else (
    echo .env file already exists
)

echo [5/5] Running demo to verify installation...
echo.
python main.py --mode demo

echo.
echo ====================================
echo   Setup Complete!
echo ====================================
echo.
echo Next steps:
echo   1. Edit .env with your AWS credentials
echo   2. Run demo:      python main.py --mode demo
echo   3. Run CLI chat:  python main.py --mode cli
echo   4. Run API:       python main.py --mode api
echo   5. Run Dashboard: streamlit run src/ui/streamlit_app.py
echo.
pause
