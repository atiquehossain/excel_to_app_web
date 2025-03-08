"""
Setup script for the Excel to Dart Code Generator.
"""
import os
import subprocess
import sys

def main():
    """Run the initial setup."""
    print("Setting up Excel to Dart Code Generator...")

    # Create virtual environment
    if not os.path.exists('venv'):
        print("Creating virtual environment...")
        subprocess.run([sys.executable, '-m', 'venv', 'venv'])

    # Activate virtual environment
    if sys.platform == 'win32':
        activate_script = os.path.join('venv', 'Scripts', 'activate.bat')
        python = os.path.join('venv', 'Scripts', 'python.exe')
    else:
        activate_script = os.path.join('venv', 'bin', 'activate')
        python = os.path.join('venv', 'bin', 'python')

    # Install requirements
    print("Installing requirements...")
    subprocess.run([python, '-m', 'pip', 'install', '-r', 'requirements.txt'])

    # Run Django migrations
    print("Running migrations...")
    subprocess.run([python, 'manage.py', 'migrate'])

    # Initialize project structure
    print("Initializing project structure...")
    subprocess.run([python, 'manage.py', 'init_project'])

    print("\nSetup completed successfully!")
    print("\nTo start the development server:")
    if sys.platform == 'win32':
        print("1. Run: .\\venv\\Scripts\\activate")
    else:
        print("1. Run: source venv/bin/activate")
    print("2. Run: python manage.py runserver")

if __name__ == '__main__':
    main() 