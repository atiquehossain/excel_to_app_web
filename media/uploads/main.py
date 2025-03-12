"""
Main script for Excel to Dart Code Generator.
"""
import os
import pandas as pd
import re
from ExcelProcessor import ExcelProcessor 
from DartCodeGenerator import DartCodeGenerator
from datetime import datetime
from num2words import num2words
from openpyxl import load_workbook

# Helper Functions
def convert_number_to_text(value):
    """Convert numeric values to text."""
    try:
        if isinstance(value, (int, float)):
            return num2words(value)
        return value
    except Exception as e:
        print(f"Error converting {value}: {e}")
        return value

def clean_column_name(name):
    """Clean column names by replacing non-alphanumeric characters with underscores."""
    return re.sub(r'[^0-9a-zA-Z]+', '_', str(name).strip()).lower()

def sanitize_key(name):
    """Sanitize keys to ensure they are valid Dart identifiers."""
    return re.sub(r'[^0-9a-zA-Z]+', '_', str(name).strip()).lower()

def write_dart_file(file_path, content):
    """Write Dart code to a file."""
    folder_path = 'generated_code'
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, file_path)
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

def load_excel_skip_hidden_rows(file_path, sheet_name):
    """Load Excel file while skipping hidden rows."""
    # Ensure we're using the correct path
    if not os.path.isabs(file_path):
        file_path = os.path.join('media', 'uploads', file_path)

    workbook = load_workbook(file_path, data_only=True)
    sheet = workbook[sheet_name]
    hidden_rows = [row for row in sheet.row_dimensions if sheet.row_dimensions[row].hidden]
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    df = df.drop(index=[row - 1 for row in hidden_rows if row <= len(df)])
    return df

def count_dropdown_and_multiple_choice_columns(df, threshold=10):
    """Count the number of dropdown and multiple-choice columns in a DataFrame."""
    dropdown_columns = [col for col in df.columns if df[col].nunique() <= threshold]
    return len(dropdown_columns), dropdown_columns

# Main Function
def process_combined_projects(file_path, sheet_name):
    # Load data
    df = load_excel_skip_hidden_rows(file_path, sheet_name)
    count, columns = count_dropdown_and_multiple_choice_columns(df, threshold=10)
    print(f"Number of dropdown/multiple-choice columns: {count}")
    print("Columns identified as dropdown/multiple-choice:", columns)

    # Clean column names
    df.columns = [clean_column_name(col) for col in df.columns]
    print(f"Cleaned columns: {df.columns}")

    # Ensure required columns for Project 2
    required_columns = ['field_names_in_english', 'data_type', 'database']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing columns for Project 2: {', '.join(missing_columns)}")

    # Convert all columns to string type and fill NaN values
    for col in df.columns:
        df[col] = df[col].fillna('').astype(str)

    # Fill missing data
    df['data_type'] = df['data_type'].fillna('').astype(str).replace('nan', '').ffill()
    df['database'] = df['database'].fillna('').astype(str).replace('nan', '').ffill()

    # Filter dropdown and multiple-choice rows
    filtered_data = df[df['data_type'].str.strip().str.lower().isin(['dropdown', 'multiple choice', 'radio', 'yes/no'])].copy()

    # Ensure all relevant columns are strings and clean
    filtered_data['field_names_in_english'] = filtered_data['field_names_in_english'].fillna('').astype(str).apply(lambda x: x.strip())

    # Flatten field names in English
    filtered_data['field_names_in_english'] = filtered_data['field_names_in_english'].fillna('').astype(str).apply(lambda x: x.strip())

    # Sanitize key directly from the full row value
    filtered_data['sanitized_key'] = filtered_data['field_names_in_english'].apply(sanitize_key)

    flattened_data = filtered_data.explode('field_names_in_english').reset_index(drop=True)

    # Group data by database
    grouped_data = flattened_data.groupby('database')['field_names_in_english'].apply(list).to_dict()

    # Generate localization data
    localization_data = {'English': {}}
    today_date = datetime.now().strftime('%Y-%m-%d')

    for _, row in flattened_data.iterrows():
        english_name = str(row['field_names_in_english']).strip()
        database_name = sanitize_key(str(row['database']).strip())  # Sanitize the database name    
        sanitized_key = f"{sanitize_key(english_name)}_{database_name}"  # Append database to the key

        localization_data['English'][sanitized_key] = english_name

    # Generate localization files field type
    content = f"/// {sheet_name} localization file - {today_date}\n\n"
    content += "class Localization {\n"
    for key, value in localization_data['English'].items():
        content += f"  String get {key}_ufind_v2 => '{value}';\n"
    content += "}\n"
    write_dart_file('en_field.dart', content)

    # Generate keys file field types
    file_path = "field_keys.dart"
    content = f"/// {sheet_name} keys file - {today_date}\n\n"
    content += "\n"
    for key in localization_data['English'].keys():
        content += f"  String get {key}_ufind_v2;\n"
    content += f"/// {sheet_name} enf keys \n"
    write_dart_file(file_path, content)

    # Generate grouped data Dart code 
    # Setupdata class
    dart_code = ""
    for database, fields in grouped_data.items():
        dart_code += f"static const String {database}_ufind_v2 = \"{database}\";\n"

    for database, fields in grouped_data.items():
        dart_code += f"else if (modelName == SetupConstant.{database}_ufind_v2) {{\n"
        for index, field in enumerate(fields, start=1):
            sanitized_field = sanitize_key(str(field).strip())
            dart_code += f"  items.add(SetupModel(Languages.getText(context)!.{sanitized_field}_{database}_ufind_v2, \"{index}\"));\n"
        dart_code += "}\n\n"

    write_dart_file("setupData.dart", dart_code)

    print("Processing completed successfully!")
    print("Files generated: en_field.dart, field_keys.dart, setupData.dart")

# Main execution
if __name__ == "__main__":
    try:   
        # Get the uploaded file path from the media/uploads directory
        upload_dir = os.path.join('media', 'uploads')
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
            
        # Get list of Excel files in the upload directory
        excel_files = [f for f in os.listdir(upload_dir) if f.endswith(('.xlsx', '.xls'))]
        
        if not excel_files:
            raise ValueError("No Excel files found in the uploads directory.")
        
        # Display available Excel files
        print("\nAvailable Excel files:")
        for i, file in enumerate(excel_files, 1):
            print(f"{i}. {file}")
        
        # Ask user to select a file
        while True:
            try:
                selection = input("\nEnter the number of the Excel file you want to work with: ")
                file_index = int(selection) - 1
                if 0 <= file_index < len(excel_files):
                    file_path = os.path.join(upload_dir, excel_files[file_index])
                    print(f"\nSelected file: {excel_files[file_index]}")
                    break
                else:
                    print(f"Invalid selection. Please enter a number between 1 and {len(excel_files)}.")
            except ValueError:
                print("Please enter a valid number.")
        
        # Get all sheet names
        sheet_names = ExcelProcessor.get_sheet_names(file_path)
        
        if not sheet_names:
            raise ValueError("No sheets found in the Excel file.")
        
        # Display available sheets
        print("\nAvailable sheets in the Excel file:")
        for i, sheet in enumerate(sheet_names, 1):
            print(f"{i}. {sheet}")
        
        # Ask user to select a sheet
        while True:
            try:
                selection = input("\nEnter the number of the sheet you want to work with: ")
                sheet_index = int(selection) - 1
                if 0 <= sheet_index < len(sheet_names):
                    sheet_name = sheet_names[sheet_index]
                    print(f"\nSelected sheet: {sheet_name}")
                    break
                else:
                    print(f"Invalid selection. Please enter a number between 1 and {len(sheet_names)}.")
            except ValueError:
                print("Please enter a valid number.")
        
        # Process the combined projects
        process_combined_projects(
            file_path=file_path,
            sheet_name=sheet_name
        )

        # Initialize and load Excel data
        processor = ExcelProcessor(file_path=file_path, sheet_name=sheet_name)
        processor.load_sheet()

        # Validate columns
        required_columns = ['questions_in_english', 'labels_in_english', 'data_type', 'database']
        df = processor.get_dataframe()

        # Validate columns and identify missing ones
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns in the sheet :::: {', '.join(missing_columns)}")

        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"Missing required columns in the sheet.")

        # Initialize Dart generator
        class_name = re.sub(r'[^\w]+', '_', sheet_name).title().replace("_", "")
        dart_generator = DartCodeGenerator(class_name, df)
        print(dart_generator.DART_WIDGET_TEMPLATE)

        # Process rows
        for index, row in df.iterrows():
            dart_generator.process_row(row, processor.clean_data_type, index)

        # Generate files
        dart_generator.generate_files()
        
    except Exception as e:
        print(f"Error: {e}")
        
