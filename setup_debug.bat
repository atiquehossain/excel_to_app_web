@echo off
echo Starting setup with debug information...

:: Check Python installation
echo Checking Python installation...
python --version
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    exit /b 1
)

:: Create virtual environment
echo.
echo Checking/Creating virtual environment...
if not exist venv (
    echo Creating new virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo Error: Failed to create virtual environment
        exit /b 1
    )
) else (
    echo Virtual environment already exists
)

:: Activate virtual environment
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo Error: Failed to activate virtual environment
    exit /b 1
)

:: Install requirements
echo.
echo Installing requirements...
pip install -r requirements.txt
if errorlevel 1 (
    echo Error: Failed to install requirements
    exit /b 1
)

:: Check Django installation
echo.
echo Checking Django installation...
python -c "import django; print(django.get_version())"
if errorlevel 1 (
    echo Error: Django is not installed correctly
    exit /b 1
)

:: Create directories
echo.
echo Creating project directories...
mkdir media 2>nul
mkdir media\uploads 2>nul
mkdir generated_code 2>nul
mkdir templates 2>nul
mkdir templates\excel_converter 2>nul
mkdir static 2>nul
echo Directory structure created

:: Check project structure
echo.
echo Checking project structure...
if not exist excel_mapper\settings.py (
    echo Error: settings.py not found
    exit /b 1
)
if not exist excel_mapper\urls.py (
    echo Error: urls.py not found
    exit /b 1
)
if not exist excel_converter\views.py (
    echo Error: views.py not found
    exit /b 1
)

:: Run Django checks
echo.
echo Running Django system checks...
python manage.py check
if errorlevel 1 (
    echo Error: Django system check failed
    exit /b 1
)

:: Make migrations
echo.
echo Making migrations...
python manage.py makemigrations
if errorlevel 1 (
    echo Error: Failed to make migrations
    exit /b 1
)

:: Run migrations
echo.
echo Running migrations...
python manage.py migrate
if errorlevel 1 (
    echo Error: Failed to apply migrations
    exit /b 1
)

:: Initialize project
echo.
echo Initializing project structure...
python manage.py init_project
if errorlevel 1 (
    echo Error: Failed to initialize project structure
    exit /b 1
)

echo.
echo Setup completed successfully!
echo.
echo Project structure:
dir /s /b excel_mapper excel_converter templates static media generated_code
echo.
echo To start the development server:
echo 1. Ensure you're in the virtual environment (venv\Scripts\activate)
echo 2. Run: python manage.py runserver
pause 