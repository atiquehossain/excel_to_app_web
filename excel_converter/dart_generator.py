"""
Dart code generation functionality.
"""
import os
import re
import pandas as pd
from datetime import datetime
from django.conf import settings

def clean_column_name(name):
    """Clean column names by replacing non-alphanumeric characters with underscores."""
    return re.sub(r'[^0-9a-zA-Z]+', '_', str(name).strip()).lower()

def sanitize_key(name):
    """Sanitize keys to ensure they are valid Dart identifiers."""
    return re.sub(r'[^0-9a-zA-Z]+', '_', str(name).strip()).lower()

def generate_dart_code(df, class_name, preview=False, metadata=None):
    """Generate Dart code from DataFrame."""
    try:
        if metadata is None:
            raise ValueError("Metadata is required")
            
        # Get column names from metadata
        database_column = metadata.get('database_column')
        if not database_column:
            raise ValueError("Database column name is required")
        
        print(f"Database column: {database_column}")  # Debug print
        print(f"Available columns: {df.columns.tolist()}")  # Debug print
        
        # Normalize column names in DataFrame
        df.columns = [col.strip().lower() for col in df.columns]
        database_column = database_column.strip().lower()
        
        if database_column not in df.columns:
            raise ValueError(f"Database column '{database_column}' not found in DataFrame. Available columns: {df.columns.tolist()}")
        
        # Get unique database values (these will be our class properties)
        database_values = df[database_column].unique()
        
        # Filter out any empty or NaN values and clean the values
        database_values = [str(val).strip() for val in database_values if pd.notna(val) and str(val).strip()]
        
        # Generate the Dart class code
        code = [f"class {class_name} {{"]
        
        # Add nullable fields
        class_name_lower = class_name.lower()
        code.append(f"  String? {class_name_lower}Id;")
        
        # Add other fields with nullable types from database values
        for db_value in database_values:
            var_name = db_value.lower().replace(' ', '_').replace('-', '_')
            code.append(f"  String? {var_name};")
        
        code.append("")
        
        # Add fromJson constructor
        code.append(f"  {class_name}.fromJson(Map<String, dynamic> json) {{")
        code.append(f"    {class_name_lower}Id = json['{class_name_lower}Id'];")
        for db_value in database_values:
            var_name = db_value.lower().replace(' ', '_').replace('-', '_')
            code.append(f"    {var_name} = json['{var_name}'];")
        code.append("  }}")
        
        code.append("")
        
        # Add getDataTypeMap method
        code.append("  Map<String, String> getDataTypeMap() {")
        code.append("    return {")
        code.append(f"      '{class_name_lower}Id': 'String',")
        for db_value in database_values:
            var_name = db_value.lower().replace(' ', '_').replace('-', '_')
            code.append(f"      '{var_name}': 'String',")
        code.append("    };")
        code.append("  }")
        
        code.append("")
        
        # Add toString method
        code.append("  @override")
        code.append("  String toString() {")
        field_strings = []
        field_strings.append(f"{class_name_lower}Id: ${class_name_lower}Id")
        for db_value in database_values:
            var_name = db_value.lower().replace(' ', '_').replace('-', '_')
            field_strings.append(f"{var_name}: ${var_name}")
        toString_content = ", ".join(field_strings)
        code.append(f"    return '{class_name}(' +")
        code.append(f"        '{toString_content}' +")
        code.append("        ');")
        code.append("  }")
        
        code.append("}")
        
        return '\n'.join(code)
        
    except Exception as e:
        print(f"Error generating Dart code: {e}")
        print(f"DataFrame columns: {df.columns.tolist()}")  # Debug print
        raise

def generate_full_model(df, class_name, preview=False, output_folder=None, question_serial_column=None):
    """Generate full model with localization and UI."""
    if output_folder is None:
        output_folder = settings.DART_SETTINGS['output_folder']
    
    # Fill missing data
    df['data_type'] = df['data_type'].fillna('').astype(str).replace('nan', '').ffill()
    df['database'] = df['database'].fillna('').astype(str).replace('nan', '').ffill()

    # Filter dropdown and multiple-choice rows
    filtered_data = df[df['data_type'].str.strip().str.lower().isin(['dropdown', 'multiple choice', 'radio'])].copy()

    # Find all language columns dynamically
    language_columns = [col for col in df.columns if col.startswith('field_names_in_')]
    if not language_columns:
        language_columns = ['field_names_in_english']  # Default to English if no language columns found

    # Ensure all relevant columns are strings and clean
    for col in language_columns:
        filtered_data[col] = filtered_data[col].fillna('').astype(str).apply(lambda x: x.strip())

    # Flatten field names in English
    filtered_data['field_names_in_english'] = filtered_data['field_names_in_english'].fillna('').astype(str).apply(lambda x: x.strip())

    # Sanitize key directly from the full row value
    filtered_data['sanitized_key'] = filtered_data['field_names_in_english'].apply(sanitize_key)

    flattened_data = filtered_data.explode('field_names_in_english').reset_index(drop=True)

    # Group data by database
    grouped_data = flattened_data.groupby('database')['field_names_in_english'].apply(list).to_dict()

    # Generate localization data dynamically based on available languages
    localization_data = {}
    for col in language_columns:
        lang = col.replace('field_names_in_', '').capitalize()
        localization_data[lang] = {}
    
    today_date = datetime.now().strftime('%Y-%m-%d')

    for _, row in flattened_data.iterrows():
        english_name = str(row['field_names_in_english']).strip()
        database_name = sanitize_key(str(row['database']).strip())  # Sanitize the database name
        sanitized_key = f"{sanitize_key(english_name)}_{database_name}"  # Append database to the key

        # Add translations for each available language
        for col in language_columns:
            lang = col.replace('field_names_in_', '').capitalize()
            value = str(row[col]).strip() if col in row else english_name
            localization_data[lang][sanitized_key] = value

    # Generate localization files field type
    generated_files = []
    for lang, translations in localization_data.items():
        lang_file = f"{lang.lower()}_field.dart"
        content = f"/// {class_name} localization file - {today_date}\n\n"
        content += "class Localization {\n"
        for key, value in translations.items():
            content += f"  String get {key}_ufind_v2 => '{value}';\n"
        content += "}\n"
        file_path = write_dart_file(lang_file, content, output_folder)
        generated_files.append(file_path)

    # Generate keys file field types
    keys_file = "field_keys.dart"
    content = f"/// {class_name} keys file - {today_date}\n\n"
    content += "\n"
    for key in localization_data['English'].keys():
        content += f"  String get {key}_ufind_v2;\n"
    content += f"/// {class_name} end keys \n"
    file_path = write_dart_file(keys_file, content, output_folder)
    generated_files.append(file_path)

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

    setup_file = "setupData.dart"
    file_path = write_dart_file(setup_file, dart_code, output_folder)
    generated_files.append(file_path)

    # Generate model and UI files
    model_content = generate_model_content(class_name, df, metadata)
    ui_content = generate_ui_content(class_name, df, question_serial_column)
    
    model_file = f"{class_name.lower()}_model.dart"
    ui_file = f"{class_name.lower()}_ui_widget.dart"
    
    model_path = write_dart_file(model_file, model_content, output_folder)
    ui_path = write_dart_file(ui_file, ui_content, output_folder)
    
    generated_files.append(model_path)
    generated_files.append(ui_path)

    if preview:
        # Return a preview of all generated files
        preview_content = f"// Generated files for {class_name}:\n\n"
        for file_path in generated_files:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
            preview_content += f"// File: {os.path.basename(file_path)}\n{file_content}\n\n"
        return preview_content
    
    return generated_files[0]  # Return the first file path

def generate_standard_model(df, class_name, preview=False, output_folder=None, question_serial_column=None):
    """Generate standard model with UI."""
    if output_folder is None:
        output_folder = settings.DART_SETTINGS['output_folder']
    
    # Generate model and UI files
    model_content = generate_model_content(class_name, df, question_serial_column)
    ui_content = generate_ui_content(class_name, df, question_serial_column)
    
    model_file = f"{class_name.lower()}_model.dart"
    ui_file = f"{class_name.lower()}_ui_widget.dart"
    
    model_path = write_dart_file(model_file, model_content, output_folder)
    ui_path = write_dart_file(ui_file, ui_content, output_folder)
    
    if preview:
        # Return a preview of both files
        with open(model_path, 'r', encoding='utf-8') as f:
            model_content = f.read()
        with open(ui_path, 'r', encoding='utf-8') as f:
            ui_content = f.read()
        
        preview_content = f"// Model file: {model_file}\n{model_content}\n\n// UI file: {ui_file}\n{ui_content}"
        return preview_content
    
    return model_path

def generate_simple_model(df, class_name, preview=False, output_folder=None, question_serial_column=None):
    """Generate a simple Dart model."""
    if output_folder is None:
        output_folder = settings.DART_SETTINGS['output_folder']
    
    # Generate code
    code = []
    code.append('import "package:flutter/material.dart";')
    code.append('')
    code.append(f'class {class_name} {{')
    
    # Add fields
    for column in df.columns:
        field_type = _get_field_type(df[column])
        code.append(f'  final {field_type} {column};')
    
    code.append('')
    
    # Add constructor
    code.append(f'  {class_name}({{')
    for column in df.columns:
        code.append(f'    required this.{column},')
    code.append('  }});')
    
    code.append('')
    
    # Add fromJson factory
    code.append(f'  factory {class_name}.fromJson(Map<String, dynamic> json) {{')
    code.append(f'    return {class_name}(')
    for column in df.columns:
        field_type = _get_field_type(df[column])
        code.append(f'      {column}: json["{column}"] as {field_type},')
    code.append('    );')
    code.append('  }')
    
    code.append('')
    
    # Add toJson method
    code.append('  Map<String, dynamic> toJson() {')
    code.append('    return {')
    for column in df.columns:
        code.append(f'      "{column}": {column},')
    code.append('    };')
    code.append('  }')
    
    code.append('}')
    
    # Join code lines
    final_code = '\n'.join(code)
    
    if preview:
        return final_code
    
    # Save to file
    output_file = os.path.join(output_folder, f'{class_name}.dart')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(final_code)
    
    return output_file

def generate_model_content(class_name, df, metadata=None):
    """Generate model content."""
    code = []
    code.append('import "package:flutter/material.dart";')
    code.append('')
    code.append(f'class {class_name} {{')
    
    if metadata:
        database_column = metadata.get('database_column')
        question_column = metadata.get('question_column')
        field_name_column = metadata.get('field_name_column')
        datatype_column = metadata.get('datatype_column')
        question_serial_column = metadata.get('question_serial_column')
        language_support = metadata.get('language_support')
        question_languages = metadata.get('question_languages', [])
        field_languages = metadata.get('field_languages', [])
        
        # Add database values
        if database_column and database_column in df.columns:
            code.append('')
            code.append('  // Database values')
            databases = df[database_column].unique()
            for db in databases:
                if pd.notna(db) and str(db).strip():
                    code.append(f'  static String {clean_column_name(db)} = "";')
        
        # Add question serial values
        if question_serial_column and question_serial_column in df.columns:
            code.append('')
            code.append('  // Question serial values')
            question_serials = df[question_serial_column].unique()
            for i, serial in enumerate(question_serials):
                if pd.notna(serial) and str(serial).strip():
                    code.append(f'  static const int QUESTION_{i+1} = {i+1}; // {serial}')
        
        # Add questions mapping
        if question_column and question_column in df.columns:
            code.append('')
            code.append('  // Questions mapping')
            code.append('  static const Map<int, String> questions = {')
            for i, row in df.iterrows():
                question = row[question_column]
                if pd.notna(question) and str(question).strip():
                    code.append(f'    {i+1}: "{question}",')
            code.append('  };')
        
        # Add field names mapping
        if field_name_column and field_name_column in df.columns:
            code.append('')
            code.append('  // Field names mapping')
            code.append('  static const Map<int, String> fieldNames = {')
            for i, row in df.iterrows():
                field_name = row[field_name_column]
                if pd.notna(field_name) and str(field_name).strip():
                    code.append(f'    {i+1}: "{field_name}",')
            code.append('  };')
        
        # Add datatype mapping
        if datatype_column and datatype_column in df.columns:
            code.append('')
            code.append('  // Field types')
            code.append('  static const Map<int, String> fieldTypes = {')
            for i, row in df.iterrows():
                datatype = row[datatype_column]
                if pd.notna(datatype) and str(datatype).strip():
                    code.append(f'    {i+1}: "{datatype}",')
            code.append('  };')
        
        # Add multilingual support if enabled
        if language_support == 'yes':
            # Add question translations
            if question_column and question_column in df.columns:
                for lang in question_languages:
                    lang_col = f'questions_in_{lang.lower()}'
                    if lang_col in df.columns:
                        code.append('')
                        code.append(f'  // Questions in {lang}')
                        code.append(f'  static const Map<int, String> questions_{lang.lower()} = {{')
                        for i, row in df.iterrows():
                            question = row[lang_col]
                            if pd.notna(question) and str(question).strip():
                                code.append(f'    {i+1}: "{question}",')
                        code.append('  };')
            
            # Add field name translations
            if field_name_column and field_name_column in df.columns:
                for lang in field_languages:
                    lang_col = f'field_names_in_{lang.lower()}'
                    if lang_col in df.columns:
                        code.append('')
                        code.append(f'  // Field names in {lang}')
                        code.append(f'  static const Map<int, String> fieldNames_{lang.lower()} = {{')
                        for i, row in df.iterrows():
                            field_name = row[lang_col]
                            if pd.notna(field_name) and str(field_name).strip():
                                code.append(f'    {i+1}: "{field_name}",')
                        code.append('  };')
        
        # Add column information
        code.append('')
        code.append('  // Column information')
        if database_column:
            code.append(f'  static const String databaseColumn = "{database_column}";')
        if question_column:
            code.append(f'  static const String questionColumn = "{question_column}";')
        if field_name_column:
            code.append(f'  static const String fieldNameColumn = "{field_name_column}";')
        if datatype_column:
            code.append(f'  static const String datatypeColumn = "{datatype_column}";')
        if question_serial_column:
            code.append(f'  static const String questionSerialColumn = "{question_serial_column}";')
        
        # Add language support information
        if language_support == 'yes':
            code.append('')
            code.append('  // Language support')
            code.append('  static const bool hasLanguageSupport = true;')
            code.append('  static const List<String> supportedQuestionLanguages = ' + str(question_languages) + ';')
            code.append('  static const List<String> supportedFieldLanguages = ' + str(field_languages) + ';')
    
    code.append('')
    code.append('  // Constructor')
    code.append(f'  {class_name}();')
    
    code.append('')
    code.append('  // Factory method to create from JSON')
    code.append(f'  factory {class_name}.fromJson(Map<String, dynamic> json) {{')
    code.append(f'    final model = {class_name}();')
    if metadata and database_column and database_column in df.columns:
        databases = df[database_column].unique()
        for db in databases:
            if pd.notna(db) and str(db).strip():
                clean_db = clean_column_name(db)
                code.append(f'    model.{clean_db} = json["{clean_db}"] ?? "";')
    code.append('    return model;')
    code.append('  }')
    
    code.append('')
    code.append('  // Convert to JSON')
    code.append('  Map<String, dynamic> toJson() {')
    code.append('    return {')
    if metadata and database_column and database_column in df.columns:
        databases = df[database_column].unique()
        for db in databases:
            if pd.notna(db) and str(db).strip():
                clean_db = clean_column_name(db)
                code.append(f'      "{clean_db}": {clean_db},')
    code.append('    };')
    code.append('  }')
    
    code.append('}')
    
    return '\n'.join(code)

def generate_ui_content(class_name, df, question_serial_column=None):
    """Generate UI content."""
    code = []
    code.append('import "package:flutter/material.dart";')
    code.append('import "package:flutter/services.dart";')
    code.append('')
    code.append(f'class {class_name}UI extends StatelessWidget {{')
    code.append('  final String label;')
    code.append('  final String question;')
    code.append('  final int fieldType;')
    code.append('  final String model;')
    code.append('  final List<dynamic> dataList;')
    code.append('  final Function(String) onChanged;')
    
    # Add question serial parameter if specified
    if question_serial_column:
        code.append('  final int questionSerial;')
    
    code.append('')
    code.append(f'  const {class_name}UI({{')
    code.append('    Key? key,')
    code.append('    required this.label,')
    code.append('    required this.question,')
    code.append('    required this.fieldType,')
    code.append('    required this.model,')
    code.append('    required this.dataList,')
    code.append('    required this.onChanged,')
    
    # Add question serial parameter to constructor if specified
    if question_serial_column:
        code.append('    required this.questionSerial,')
    
    code.append('  }}) : super(key: key);')
    code.append('')
    code.append('  @override')
    code.append('  Widget build(BuildContext context) {')
    code.append('    return Column(')
    code.append('      crossAxisAlignment: CrossAxisAlignment.start,')
    code.append('      children: [')
    
    # Add question serial display if specified
    if question_serial_column:
        code.append('        // Question serial')
        code.append('        Row(')
        code.append('          children: [')
        code.append('            Container(')
        code.append('              padding: EdgeInsets.symmetric(horizontal: 8, vertical: 4),')
        code.append('              decoration: BoxDecoration(')
        code.append('                color: Colors.blue,')
        code.append('                borderRadius: BorderRadius.circular(4),')
        code.append('              ),')
        code.append('              child: Text(')
        code.append('                questionSerial.toString(),')
        code.append('                style: TextStyle(')
        code.append('                  color: Colors.white,')
        code.append('                  fontWeight: FontWeight.bold,')
        code.append('                ),')
        code.append('              ),')
        code.append('            ),')
        code.append('            SizedBox(width: 8),')
        code.append('            Expanded(')
        code.append('              child: Text(')
        code.append('                question,')
        code.append('                style: TextStyle(')
        code.append('                  fontSize: 16,')
        code.append('                  fontWeight: FontWeight.bold,')
        code.append('                ),')
        code.append('              ),')
        code.append('            ),')
        code.append('          ],')
        code.append('        ),')
    else:
        code.append('        Text(')
        code.append('          question,')
        code.append('          style: TextStyle(')
        code.append('            fontSize: 16,')
        code.append('            fontWeight: FontWeight.bold,')
        code.append('          ),')
        code.append('        ),')
    
    code.append('        SizedBox(height: 8),')
    code.append('        _buildField(),')
    code.append('        SizedBox(height: 16),')
    code.append('      ],')
    code.append('    );')
    code.append('  }')
    code.append('')
    code.append('  Widget _buildField() {')
    code.append('    switch (fieldType) {')
    code.append('      case AppConstant.FieldType_dropdown:')
    code.append('        return _buildDropdown();')
    code.append('      case AppConstant.FieldType_multiple_choice:')
    code.append('        return _buildMultipleChoice();')
    code.append('      case AppConstant.FieldType_radio:')
    code.append('        return _buildRadioGroup();')
    code.append('      case AppConstant.FieldType_EditText:')
    code.append('        return _buildTextField();')
    code.append('      case AppConstant.FieldType_Image:')
    code.append('        return _buildImagePicker();')
    code.append('      default:')
    code.append('        return _buildTextField();')
    code.append('    }')
    code.append('  }')
    code.append('')
    code.append('  Widget _buildDropdown() {')
    code.append('    return DropdownButtonFormField<String>(')
    code.append('      decoration: InputDecoration(')
    code.append('        labelText: label,')
    code.append('        border: OutlineInputBorder(),')
    code.append('      ),')
    code.append('      value: model.isNotEmpty ? model : null,')
    code.append('      items: dataList.map((item) {')
    code.append('        return DropdownMenuItem(')
    code.append('          value: item.toString(),')
    code.append('          child: Text(item.toString()),')
    code.append('        );')
    code.append('      }).toList(),')
    code.append('      onChanged: (value) {')
    code.append('        if (value != null) {')
    code.append('          onChanged(value);')
    code.append('        }')
    code.append('      },')
    code.append('    );')
    code.append('  }')
    code.append('')
    code.append('  Widget _buildMultipleChoice() {')
    code.append('    // Implementation for multiple choice')
    code.append('    return Column(')
    code.append('      crossAxisAlignment: CrossAxisAlignment.start,')
    code.append('      children: [')
    code.append('        Text(label),')
    code.append('        // Add multiple choice implementation here')
    code.append('      ],')
    code.append('    );')
    code.append('  }')
    code.append('')
    code.append('  Widget _buildRadioGroup() {')
    code.append('    // Implementation for radio group')
    code.append('    return Column(')
    code.append('      crossAxisAlignment: CrossAxisAlignment.start,')
    code.append('      children: [')
    code.append('        Text(label),')
    code.append('        // Add radio group implementation here')
    code.append('      ],')
    code.append('    );')
    code.append('  }')
    code.append('')
    code.append('  Widget _buildTextField() {')
    code.append('    return TextFormField(')
    code.append('      decoration: InputDecoration(')
    code.append('        labelText: label,')
    code.append('        border: OutlineInputBorder(),')
    code.append('      ),')
    code.append('      initialValue: model,')
    code.append('      onChanged: onChanged,')
    code.append('    );')
    code.append('  }')
    code.append('')
    code.append('  Widget _buildImagePicker() {')
    code.append('    // Implementation for image picker')
    code.append('    return Column(')
    code.append('      crossAxisAlignment: CrossAxisAlignment.start,')
    code.append('      children: [')
    code.append('        Text(label),')
    code.append('        // Add image picker implementation here')
    code.append('      ],')
    code.append('    );')
    code.append('  }')
    code.append('}')
    code.append('')
    code.append('class AppConstant {')
    code.append('  static const int FieldType_dropdown = 1;')
    code.append('  static const int FieldType_multiple_choice = 2;')
    code.append('  static const int FieldType_radio = 3;')
    code.append('  static const int FieldType_EditText = 4;')
    code.append('  static const int FieldType_Image = 5;')
    code.append('  static const String SEPERATOR = "_";')
    code.append('}')
    
    return '\n'.join(code)

def _get_field_type(series):
    """Determine the Dart field type based on the data."""
    if series.dtype == 'int64':
        return 'int'
    elif series.dtype == 'float64':
        return 'double'
    elif series.nunique() <= 10:  # Potential enum/dropdown
        return 'String'  # For simplicity, use String for now
    else:
        return 'String' 