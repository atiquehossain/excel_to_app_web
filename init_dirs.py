"""
Initialize required directories for the Excel to Dart Code Generator.
"""
import os

def init_directories():
    """Create all required directories."""
    # Create media directory
    os.makedirs('media/uploads', exist_ok=True)
    print("Created media/uploads directory")
    
    # Create generated_code directory
    os.makedirs('generated_code', exist_ok=True)
    print("Created generated_code directory")
    
    # Create templates directory
    os.makedirs('templates/excel_converter', exist_ok=True)
    print("Created templates/excel_converter directory")
    
    # Create static directory
    os.makedirs('static', exist_ok=True)
    print("Created static directory")
    
    print("All directories created successfully!")

if __name__ == "__main__":
    init_directories() 