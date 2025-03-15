# Excel to Dart Model Converter

This project converts Excel files into Dart model classes. It's designed to make it easy to transform your Excel data into usable Dart code.

## How It Works

1. **Upload Excel File**: Upload your Excel file through the web interface
2. **Select Sheet**: Choose which sheet contains your data
3. **Preview Code**: See the generated Dart code before downloading
4. **Download**: Get your Dart model class ready to use

## Core Functions Explained

### Excel Processing (`utils.py`)

1. `get_excel_path(filename)`:
   - Takes a filename and returns the full path where Excel files are stored
   - Example: `uploads/myfile.xlsx`

2. `normalize_sheet_name(name)`:
   - Cleans up sheet names by removing spaces and special characters
   - Example: "My Sheet!" → "MySheet"

3. `get_excel_sheets(file_path)`:
   - Gets a list of all sheet names from an Excel file
   - Example: ["Sheet1", "Data", "Summary"]

4. `process_excel_file(file_path, sheet_name)`:
   - Main function that reads and processes the Excel file
   - Cleans column names and converts data to proper format
   - Returns a DataFrame ready for code generation

5. `sanitize_key(name)`:
   - Makes strings safe to use as Dart variable names
   - Example: "User Name" → "user_name"

### Dart Code Generation (`dart_generator.py`)

1. `generate_dart_code(df, class_name, preview, metadata)`:
   - Main function that generates the Dart class code
   - Creates:
     - Class declaration
     - Nullable fields
     - fromJson constructor
     - getDataTypeMap method
     - toString method

## Example Usage

Your Excel file structure should look like this:
```excel
| database        | field_name | data_type |
|----------------|------------|-----------|
| event_name     | Event Name | String    |
| meeting_with   | Met With   | String    |
| total_number   | Total      | int       |
```

This will generate a Dart class like:
```dart
class MyModel {
  String? mymodelId;
  String? event_name;
  String? meeting_with;
  String? total_number;

  MyModel.fromJson(Map<String, dynamic> json) {
    mymodelId = json['mymodelId'];
    event_name = json['event_name'];
    meeting_with = json['meeting_with'];
    total_number = json['total_number'];
  }

  Map<String, String> getDataTypeMap() {
    return {
      'mymodelId': 'String',
      'event_name': 'String',
      'meeting_with': 'String',
      'total_number': 'String',
    };
  }

  @override
  String toString() {
    return 'MyModel(mymodelId: $mymodelId, event_name: $event_name, meeting_with: $meeting_with, total_number: $total_number)';
  }
}
```

## Requirements

- Python 3.7+
- pandas
- Django
- openpyxl

## Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run migrations: `python manage.py migrate`
4. Start server: `python manage.py runserver`

## Notes

- All fields are generated as nullable (`String?`)
- Column names are automatically cleaned and converted to valid Dart identifiers
- The generated code includes proper toString and JSON serialization methods

## Features

- Convert Excel data to Dart/Flutter code
- Support for multiple field types (Dropdown, Multiple choice, Radio, Text, Number, Image)
- Multi-language support (English, Tamil, Sinhala)
- GUI and CLI interfaces
- Customizable templates
- Hidden row handling
- Data type validation

## Project Structure

```
excel-mapper/
├── core/
│   ├── __init__.py
│   ├── excel_processor.py
│   └── dart_generator.py
├── generators/
│   ├── __init__.py
│   ├── widget_generator.py
│   └── model_generator.py
├── processors/
│   ├── __init__.py
│   └── data_processor.py
├── utils/
│   ├── __init__.py
│   └── helpers.py
├── config/
│   └── settings.py
├── tests/
│   └── __init__.py
├── main.py
├── main_gui_version.py
└── requirements.txt
```

## Configuration

Create a `config.yaml` file in the root directory to customize the behavior:

```yaml
excel:
  default_sheet: "Sheet1"
  skip_hidden_rows: true

dart:
  output_folder: "generated_code"
  template_folder: "templates"
  null_safety: true

languages:
  - English
  - Tamil
  - Sinhala
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Flutter team for the amazing framework
- Pandas team for Excel processing capabilities
- All contributors who have helped shape this project 

# Excel to Flutter App Generator

A Django web application that converts Excel files into complete Flutter app code, including models, UI widgets, and language support.

## Features

- Excel file upload and processing
- Multiple sheet support
- Automatic Dart model generation
- UI widget generation
- List page generation
- Multi-language support
- Download generated code

## How It Works

### Excel Processing with Pandas: Step by Step

The application uses pandas for sophisticated Excel file handling. Here's a detailed breakdown:

1. **Initial File Reading**:
   ```python
   # Create Excel file object for reading sheets
   excel_file = pd.ExcelFile(file_path)
   
   # Get all sheet names
   sheet_names = excel_file.sheet_names
   ```

2. **Sheet Selection and Loading**:
   ```python
   # Read specific sheet into DataFrame
   df = pd.read_excel(file_path, sheet_name=sheet_name)
   
   # Example DataFrame structure:
   # | database_column | field_name | data_type |
   # |----------------|------------|-----------|
   # | event_name     | Event Name | String    |
   # | meeting_with   | Met With   | String    |
   ```

3. **Column Name Cleaning**:
   ```python
   # Clean and standardize column names
   df.columns = (
       df.columns.str.strip()           # Remove leading/trailing spaces
               .str.lower()             # Convert to lowercase
               .str.replace(r'\s+', '_') # Replace spaces with underscore
               .str.replace(r'[^\w]', '') # Remove special characters
   )
   
   # Result: 'Event Name' -> 'event_name'
   ```

4. **Data Type Conversion and Cleaning**:
   ```python
   # Handle missing values and convert to strings
   for col in df.columns:
       # Replace NaN with empty string and convert to string
       df[col] = df[col].fillna('').astype(str)
       
       # Strip whitespace from all values
       df[col] = df[col].str.strip()
   ```

5. **Row Processing**:
   ```python
   # Remove completely empty rows
   df = df.dropna(how='all')
   
   # Iterate through rows for processing
   for index, row in df.iterrows():
       # Access values by column name
       database_value = row['database_column']
       field_name = row['field_name']
       data_type = row['data_type']
   ```

6. **Data Validation**:
   ```python
   # Check for required columns
   required_columns = ['database_column', 'field_name', 'data_type']
   missing_columns = [col for col in required_columns if col not in df.columns]
   
   # Validate data types
   invalid_rows = []
   for index, row in df.iterrows():
       if pd.isna(row['data_type']):
           invalid_rows.append(index + 2)  # Excel row numbers start at 1
   ```

7. **Language Support Processing**:
   ```python
   # Handle multiple language columns
   language_columns = [col for col in df.columns if col.startswith('questions_in_')]
   
   for lang_col in language_columns:
       # Extract language name
       language = lang_col.replace('questions_in_', '')
       
       # Process translations
       df[f'translated_{language}'] = df[lang_col].fillna(df['field_name'])
   ```

8. **Data Export for Code Generation**:
   ```python
   # Convert DataFrame to dictionary for Dart code generation
   for index, row in df.iterrows():
       field_data = {
           'name': row['database_column'],
           'type': row['data_type'],
           'description': row['field_name'],
           'translations': {
               lang: row[f'questions_in_{lang}']
               for lang in languages
               if f'questions_in_{lang}' in row
           }
       }
       fields.append(field_data)
   ```

### Common Pandas Operations Used

1. **DataFrame Creation**:
   - `pd.ExcelFile()`: Create Excel file object
   - `pd.read_excel()`: Read Excel into DataFrame

2. **Column Operations**:
   - `df.columns`: Access column names
   - `str.strip()`: Remove whitespace
   - `str.lower()`: Convert to lowercase
   - `str.replace()`: Replace patterns

3. **Row Operations**:
   - `df.iterrows()`: Iterate through rows
   - `df.dropna()`: Remove empty rows
   - `df.fillna()`: Fill missing values

4. **Data Cleaning**:
   - `astype(str)`: Convert to string type
   - `pd.isna()`: Check for missing values
   - `str.strip()`: Remove whitespace

5. **Data Access**:
   - `row['column_name']`: Access cell value
   - `df['column_name']`: Access column
   - `df.loc[]`: Label-based indexing

## Installation

1. Clone the repository:
   ```