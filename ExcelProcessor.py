import pandas as pd
import re
from openpyxl import load_workbook

class ExcelProcessor:
    """Handles processing of the Excel file and data extraction."""
    DATA_TYPE_MAPPINGS = {
        "dropdown": "Dropdown",
        "multiple choice": "Multiple choice",
        "radio": "radio",
        "number": "Number",
        "text": "Text",
        "image": "Image",
    }

    def __init__(self, file_path, sheet_name):
        self.file_path = file_path
        self.sheet_name = sheet_name
        self.df = None

    def load_excel_skip_hidden_rows(self):
        """Load Excel file while skipping hidden rows."""
        # Load the workbook and sheet
        workbook = load_workbook(self.file_path, data_only=True)
        sheet = workbook[self.sheet_name]

        # Identify hidden rows
        hidden_rows = [row for row in sheet.row_dimensions if sheet.row_dimensions[row].hidden]

        # Read the Excel file with pandas
        df = pd.read_excel(self.file_path, sheet_name=self.sheet_name)

        # Drop hidden rows by their index (Excel row numbers are 1-based)
        df = df.drop(index=[row - 1 for row in hidden_rows if row <= len(df)])
        
        # Convert all object columns to string to avoid .str accessor errors
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].astype(str)
        
        return df

    def load_sheet(self):
        """Loads and cleans the Excel sheet."""
        # Call the load_excel_skip_hidden_rows method within the class
        self.df = self.load_excel_skip_hidden_rows()
        
        # Clean column names: strip, lower, replace spaces with underscores, and remove non-alphanumeric characters
        self.df.columns = (
            self.df.columns.str.strip()
                        .str.lower()
                        .str.replace(r'\s+', '_', regex=True)
                        .str.replace(r'[^\w]', '', regex=True)
        )
        
        # Convert all columns to string type to avoid .str accessor errors
        for col in self.df.columns:
            self.df[col] = self.df[col].fillna('').astype(str)
        
        return self.df

    def clean_data_type(self, data_type):
        """Cleans and maps the data type to a standardized format."""
        if pd.isna(data_type) or not isinstance(data_type, str):
            data_type = str(data_type)
        
        data_type = data_type.strip().lower()
        
        # Map to standardized data types
        for key, value in self.DATA_TYPE_MAPPINGS.items():
            if key in data_type:
                return value
        
        # Default to text if no match is found
        return "Text"

    def get_dataframe(self):
        """Returns the processed DataFrame."""
        return self.df

    @staticmethod
    def get_sheet_names(file_path):
        """Get all sheet names from an Excel file."""
        try:
            # Use pandas to get sheet names
            excel_file = pd.ExcelFile(file_path)
            sheet_names = excel_file.sheet_names
            return sheet_names
        except Exception as e:
            print(f"Error getting sheet names: {e}")
            return []



