"""
Dart code generation functionality.
This module handles the conversion of Excel data into Dart class code,
creating properly formatted Dart models with JSON serialization support.
"""
import re
import pandas as pd

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

def generate_dart_code(df, class_name, preview=False, metadata=None):
    """
    Generates a complete Dart class from DataFrame data.
    
    This function creates a Dart class with:
    1. Nullable fields for each database value
    2. A fromJson constructor for JSON deserialization
    3. A getDataTypeMap method for type information
    4. A toString method for debugging
    
    Args:
        df (pandas.DataFrame): The processed Excel data
        class_name (str): Name for the Dart class (e.g., 'UserModel')
        preview (bool): Whether this is for preview only
        metadata (dict): Additional information like database column name
    
    Returns:
        str: Generated Dart class code
    
    Example:
        >>> metadata = {'database_column': 'database'}
        >>> df = pd.DataFrame({'database': ['name', 'age']})
        >>> print(generate_dart_code(df, 'User', metadata=metadata))
        class User {
          String? userId;
          String? name;
          String? age;
          ...
        }
    
    Notes:
        - All fields are generated as nullable (String?)
        - The class includes proper JSON serialization support
        - Field names are sanitized to be valid Dart identifiers
    """
    try:
        if metadata is None:
            raise ValueError("Metadata is required")
            
        # Get column names from metadata
        database_column = metadata.get('database_column')
        if not database_column:
            raise ValueError("Database column name is required")
        
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
        
        # Add fromJson constructor for JSON deserialization
        code.append(f"  {class_name}.fromJson(Map<String, dynamic> json) {{")
        code.append(f"    {class_name_lower}Id = json['{class_name_lower}Id'];")
        for db_value in database_values:
            var_name = db_value.lower().replace(' ', '_').replace('-', '_')
            code.append(f"    {var_name} = json['{var_name}'];")
        code.append("  }}")
        
        code.append("")
        
        # Add getDataTypeMap method for type information
        code.append("  Map<String, String> getDataTypeMap() {")
        code.append("    return {")
        code.append(f"      '{class_name_lower}Id': 'String',")
        for db_value in database_values:
            var_name = db_value.lower().replace(' ', '_').replace('-', '_')
            code.append(f"      '{var_name}': 'String',")
        code.append("    };")
        code.append("  }")
        
        code.append("")
        
        # Add toString method for debugging
        code.append("  @override")
        code.append("  String toString() {")
        field_strings = []
        field_strings.append(f"{class_name_lower}Id: ${class_name_lower}Id")
        for db_value in database_values:
            var_name = db_value.lower().replace(' ', '_').replace('-', '_')
            field_strings.append(f"{var_name}: ${var_name}")
        toString_content = ", ".join(field_strings)
        code.append(f"    return '{class_name}({toString_content})';")
        code.append("  }")
        
        code.append("}")
        
        return '\n'.join(code)
        
    except Exception as e:
        print(f"Error generating Dart code: {e}")
        print(f"DataFrame columns: {df.columns.tolist()}")  # Debug print
        raise 