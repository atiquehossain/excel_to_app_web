"""
Utility functions for excel_converter app.
"""
import os
import re
import pandas as pd
from django.conf import settings
from openpyxl import load_workbook
from datetime import datetime

def get_excel_path(filename):
    """Get the full path for an Excel file."""
    return os.path.join(settings.MEDIA_ROOT, 'uploads', filename)

def get_excel_sheets(file_path):
    """Get all sheet names from an Excel file."""
    try:
        # Use pandas to get sheet names
        print(f"Attempting to get sheet names from: {file_path}")
        excel_file = pd.ExcelFile(file_path)
        sheet_names = excel_file.sheet_names
        print(f"Found sheets: {sheet_names}")
        return sheet_names
    except Exception as e:
        print(f"Error getting sheet names: {e}")
        return []

def normalize_sheet_name(name):
    """Normalize sheet name by removing spaces and special characters."""
    return re.sub(r'[^a-zA-Z0-9]', '', str(name).strip())

def process_excel_file(file_path, sheet_name=None):
    """Process the Excel file and return a DataFrame."""
    # Ensure we're using the correct path
    if not os.path.isabs(file_path):
        file_path = get_excel_path(os.path.basename(file_path))
    
    try:
        # Get sheet names if not provided
        if not sheet_name:
            excel_file = pd.ExcelFile(file_path)
            sheet_names = excel_file.sheet_names
            if sheet_names:
                sheet_name = sheet_names[0]  # Use the first sheet by default
            else:
                raise ValueError("No sheets found in the Excel file.")

        # Verify sheet exists with normalized comparison
        excel_file = pd.ExcelFile(file_path)
        normalized_sheet_name = normalize_sheet_name(sheet_name)
        available_sheets = excel_file.sheet_names
        
        # Try to find a matching sheet
        matching_sheet = None
        for available_sheet in available_sheets:
            if normalize_sheet_name(available_sheet) == normalized_sheet_name:
                matching_sheet = available_sheet
                break
        
        if not matching_sheet:
            raise ValueError(f"Sheet '{sheet_name}' not found in the Excel file. Available sheets: {', '.join(available_sheets)}")

        # Load workbook and get hidden rows
        workbook = load_workbook(file_path, data_only=True)
        sheet = workbook[matching_sheet]
        hidden_rows = [row for row in sheet.row_dimensions if sheet.row_dimensions[row].hidden]
        
        # Read Excel file
        df = pd.read_excel(file_path, sheet_name=matching_sheet)
        
        # Skip hidden rows if configured
        if settings.EXCEL_SETTINGS['skip_hidden_rows']:
            df = df.drop(index=[row - 1 for row in hidden_rows if row <= len(df)])
        
        # Clean column names
        df.columns = (
            df.columns.str.strip()
                    .str.lower()
                    .str.replace(r'\s+', '_', regex=True)
                    .str.replace(r'[^\w]', '', regex=True)
        )
        
        # Convert all columns to string type to avoid .str accessor errors
        for col in df.columns:
            df[col] = df[col].fillna('').astype(str)
        
        return df
        
    except Exception as e:
        raise ValueError(f"Error processing Excel file: {str(e)}")

def clean_column_name(name):
    """Clean column names by replacing non-alphanumeric characters with underscores."""
    return re.sub(r'[^0-9a-zA-Z]+', '_', str(name).strip()).lower()

def count_dropdown_and_multiple_choice_columns(df, threshold=10):
    """Count the number of dropdown and multiple-choice columns in a DataFrame."""
    dropdown_columns = [col for col in df.columns if df[col].nunique() <= threshold]
    return len(dropdown_columns), dropdown_columns

def sanitize_key(name):
    """Sanitize keys to ensure they are valid Dart identifiers."""
    return re.sub(r'[^0-9a-zA-Z]+', '_', str(name).strip()).lower() 