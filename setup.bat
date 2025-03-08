@echo off
echo Setting up Excel to Dart Code Generator...

:: Create virtual environment
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Install requirements
echo Installing requirements...
pip install -r requirements.txt

:: Create necessary directories
echo Creating directories...
mkdir media 2>nul
mkdir media\uploads 2>nul
mkdir generated_code 2>nul
mkdir templates\excel_converter 2>nul
mkdir static 2>nul

:: Run Django migrations
echo Running migrations...
python manage.py migrate

:: Initialize project structure
echo Initializing project structure...
python manage.py init_project

echo.
echo Setup completed successfully!
echo.
echo To start the development server:
echo 1. Run: venv\Scripts\activate
echo 2. Run: python manage.py runserver 