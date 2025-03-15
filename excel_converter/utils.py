"""
Utility functions for processing Excel files and preparing data for Dart code generation.
This module handles all Excel-related operations like reading files, cleaning data,
and preparing it for code generation.
"""
import os
import re
import pandas as pd
from django.conf import settings
from openpyxl import load_workbook

def get_excel_path(filename):
    """
    Constructs the full path where an uploaded Excel file is stored.
    
    Args:
        filename (str): Name of the Excel file (e.g., 'data.xlsx')
    
    Returns:
        str: Full path to the Excel file (e.g., '/media/uploads/data.xlsx')
    
    Example:
        >>> get_excel_path('mydata.xlsx')
        '/media/uploads/mydata.xlsx'
    """
    return os.path.join(settings.MEDIA_ROOT, 'uploads', filename)

def normalize_sheet_name(name):
    """
    Cleans up Excel sheet names by removing spaces and special characters.
    This helps match sheet names regardless of formatting differences.
    
    Args:
        name (str): Original sheet name (e.g., 'My Sheet!')
    
    Returns:
        str: Cleaned sheet name (e.g., 'MySheet')
    
    Example:
        >>> normalize_sheet_name('My Data Sheet!')
        'MyDataSheet'
    """
    return re.sub(r'[^a-zA-Z0-9]', '', str(name).strip())

def get_excel_sheets(file_path):
    """
    Gets a list of all sheet names from an Excel file.
    
    Args:
        file_path (str): Path to the Excel file
    
    Returns:
        list: List of sheet names found in the Excel file
    
    Example:
        >>> get_excel_sheets('data.xlsx')
        ['Sheet1', 'Data', 'Summary']
    """
    try:
        excel_file = pd.ExcelFile(file_path)
        sheet_names = excel_file.sheet_names
        return sheet_names
    except Exception as e:
        print(f"Error getting sheet names: {e}")
        return []

def process_excel_file(file_path, sheet_name=None):
    """
    Main function that reads and processes an Excel file.
    It handles sheet selection, data cleaning, and format conversion.
    
    Args:
        file_path (str): Path to the Excel file
        sheet_name (str, optional): Name of the sheet to process. If None, uses first sheet.
    
    Returns:
        pandas.DataFrame: Processed data ready for code generation
    
    Example:
        >>> df = process_excel_file('data.xlsx', 'Sheet1')
        >>> df.columns
        ['event_name', 'meeting_with', 'total_number']
    
    Notes:
        - Converts all column names to lowercase and replaces spaces with underscores
        - Handles sheet name matching regardless of case or special characters
        - Converts all data to string format for consistency
    """
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

        # Read Excel file with the matched sheet name
        df = pd.read_excel(file_path, sheet_name=matching_sheet)
        
        # Clean column names
        df.columns = (
            df.columns.str.strip()
                    .str.lower()
                    .str.replace(r'\s+', '_', regex=True)
                    .str.replace(r'[^\w]', '', regex=True)
        )
        
        # Convert all columns to string type
        for col in df.columns:
            df[col] = df[col].fillna('').astype(str)
        
        return df
        
    except Exception as e:
        raise ValueError(f"Error processing Excel file: {str(e)}")

def sanitize_key(name):
    """
    Makes strings safe to use as Dart variable names by removing invalid characters.
    
    Args:
        name (str): Original string (e.g., 'User Name!')
    
    Returns:
        str: Valid Dart identifier (e.g., 'user_name')
    
    Example:
        >>> sanitize_key('User Name!')
        'user_name'
    """
    return re.sub(r'[^0-9a-zA-Z]+', '_', str(name).strip()).lower() 