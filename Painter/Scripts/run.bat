@echo off

REM Ensure Python and pip are installed
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python is not installed. Please install it from https://www.python.org/
    exit /b 1
)

REM Ensure pip is up to date
python -m ensurepip
python -m pip install --upgrade pip

REM Create virtual environment if it doesn’t exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate

@REM REM Install dependencies if requirements.txt exists
@REM if exist requirements.txt (
@REM     echo Installing dependencies...
@REM     pip install -r requirements.txt
@REM )

REM Run painter_app.py
echo Running painter_app.py...
python painter_app.py

endlocal