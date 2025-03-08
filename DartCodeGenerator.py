import pandas as pd
import re
import os
from widgetTemp import DartWidgetGenerator
from TemplateProvider import TemplateProvider 
from datetime import datetime

class DartCodeGenerator:
    """Generates Dart code for widgets, models, and localization."""

    # Mapping of data types to field types and Dart types
    DATA_TYPE_TO_FIELD_TYPE = {
        "Dropdown": "AppConstant.FieldType_dropdown",
        "Multiple choice": "AppConstant.FieldType_multiple_choice",
        "radio": "AppConstant.FieldType_radio",
        "Number": "AppConstant.FieldType_EditText",
        "Text": "AppConstant.FieldType_EditText",
        "Image": "AppConstant.FieldType_Image"
    }

    DATA_TYPE_TO_DART_TYPE = {
        "Dropdown": "String",
        "Multiple choice": "String",
        "radio": "int",
        "Number": "double",
        "Text": "String",
        "Image": "String",
    }

    def __init__(self, class_name, df, output_folder='ui_and_languages'):
        """Initializes the DartCodeGenerator instance with necessary parameters and folder setup."""
        self.class_name = class_name
        self.df = df
        self.localization_data = {"Tamil": {}, "Sinhala": {}, "English": {}}
        self.dart_widgets = []
        self.model_fields = []
        self.constructor_params = []
        self.from_json = []
        self.to_json = []
        self.to_string = []
        self.output_folder = output_folder

        # Initialize the widget template
        self.DART_WIDGET_TEMPLATE = ""

        # Create output folder if it doesn't exist
        os.makedirs(self.output_folder, exist_ok=True)

    def _sanitize_string(self, value):
        """Sanitizes a string for Dart compatibility."""
        if pd.isna(value) or value is None:
            return ""
        
        value = str(value).strip()
        # Replace special characters with underscores
        sanitized = re.sub(r'[^a-zA-Z0-9]', '_', value)
        # Remove consecutive underscores
        sanitized = re.sub(r'_+', '_', sanitized)
        # Remove leading and trailing underscores
        sanitized = sanitized.strip('_')
        # Ensure it starts with a letter
        if sanitized and not sanitized[0].isalpha():
            sanitized = 'a' + sanitized
        # Handle empty string
        if not sanitized:
            sanitized = 'empty'
        return sanitized.lower()

    def _get_data_list_conditionally_const(self, field_type, model):
        """Returns the corresponding data list or null based on the field type."""
        if field_type in ['AppConstant.FieldType_multiple_choice', 'AppConstant.FieldType_dropdown', 'AppConstant.FieldType_radio']:
            return f"SetupConstant.{model}"
        else:
            return "null"  

    def _get_data_list_conditionally_type_and_model(self, field_type, model):
        """Returns the corresponding function to fetch the data list based on the field type."""
        if field_type == 'AppConstant.FieldType_multiple_choice':
            return f"SetupData.SetupData.getCheklistItems(context, SetupConstant.{model}_ufind_v2)"
        elif field_type == 'AppConstant.FieldType_dropdown':
            return f"SetupData.getDropDownItems(context, SetupConstant.{model}_ufind_v2)"
        elif field_type == 'AppConstant.FieldType_radio':
            return f"SetupData.getCheklistItemsWithoutFuture(context, SetupConstant.{model}_ufind_v2)"
        else:
            return "null" 

    def process_row(self, row, clean_data_type, row_number):
        """Processes a single row of data to generate widget and model information."""
        try:
            # Convert all values to strings and handle NaN values
            row_dict = {}
            for col in row.index:
                row_dict[col] = str(row[col]).strip() if not pd.isna(row[col]) else ""
            
            # Extract data from the row
            question_english = row_dict.get('questions_in_english', '')
            label_english = row_dict.get('labels_in_english', '')
            data_type = clean_data_type(row_dict.get('data_type', ''))
            database = row_dict.get('database', '')
            
            # Skip empty rows
            if not question_english or not label_english or not data_type:
                return
            
            # Generate field name
            field_name = self._sanitize_string(label_english)
            
            # Get field type and Dart type
            field_type = self.DATA_TYPE_TO_FIELD_TYPE.get(data_type, "AppConstant.FieldType_EditText")
            dart_type = self.DATA_TYPE_TO_DART_TYPE.get(data_type, "String")
            
            # Add to model fields
            self.model_fields.append(f"  final {dart_type} {field_name};")
            
            # Add to constructor parameters
            self.constructor_params.append(f"    required this.{field_name},")
            
            # Add to fromJson method
            self.from_json.append(f"      {field_name}: json['{field_name}'] as {dart_type},")
            
            # Add to toJson method
            self.to_json.append(f"      '{field_name}': {field_name},")
            
            # Add to toString method
            self.to_string.append(f"      '{field_name}: ${{this.{field_name}}}\\n' +")
            
            # Add to localization data
            for lang in ['Tamil', 'Sinhala', 'English']:
                lang_key = f"questions_in_{lang.lower()}"
                if lang_key in row_dict and row_dict[lang_key]:
                    self.localization_data[lang][field_name] = row_dict[lang_key]
            
            # Generate widget template
            question_key = self._sanitize_string(question_english)
            label_key = self._sanitize_string(label_english)
            
            # Append the widget code to the list for Dart widget generation
            self.dart_widgets.append(
                f"""
                        /// Question number  = {row_number + 2}
                        build{self.class_name}Question(
                        number: {row_number + 2},
                        condition: true, 
                        widget: {self.class_name}UI(
                            label: Languages.getText(context)!.{label_key}_ufind_v2,
                            question: Languages.getText(context)!.{question_key}_ufind_v2,
                            fieldType: {field_type},
                            model: {self.class_name.lower()}.{database},
                            dataList: {self._get_data_list_conditionally_type_and_model(field_type, database)},
                            onChanged: (value) {{
                                {self.class_name.lower()}.{database} = value;
                                selectedOptions[Languages.getText(context)!.{question_key}_ufind_v2] = 
                                    {self._get_data_list_conditionally_const(field_type, database)}_ufind_v2
                                    + AppConstant.SEPERATOR 
                                    + value;
                            }},
                        ),
                        ),
                """
            )
            
        except Exception as e:
            print(f"Error processing row: {e}")

    def generate_files(self):
        """Generates and saves Dart widget, model, and localization files."""

        # Generate the Dart widget code
        self.DART_WIDGET_TEMPLATE = DartWidgetGenerator.generate_widget_template(
            self.class_name, self.class_name.lower(), "\n".join(self.dart_widgets)
        )

        # Generate the Dart model code
        dart_model_code = TemplateProvider.get_model_template().format(
            class_name=self.class_name,
            fields="\n  ".join(self.model_fields),
            constructor_params="\n    ".join(self.constructor_params),
            from_json="\n      ".join([f"{field.strip()};" for field in self.from_json]),
            to_json="\n      ".join(self.to_json),
            to_string=", ".join(self.to_string)
        )

        # Write the widget code to the file
        with open(os.path.join(self.output_folder, f"{self.class_name.lower()}_ui_widget.dart"), 'w', encoding='utf-8') as f:
            f.write(self.DART_WIDGET_TEMPLATE)

        # Write the model code to the file
        with open(os.path.join(self.output_folder, f"{self.class_name.lower()}_model.dart"), 'w', encoding='utf-8') as f:
            f.write(dart_model_code)

        # Write the localization files for each language
        root_sheet_name = self.class_name
        today_date = datetime.now().strftime('%Y-%m-%d')

        for lang, translations in self.localization_data.items():
            localization_fields = [
                f'String get {key}_ufind_v2 => "{self._sanitize_string(value)}";'
                for key, value in translations.items()
            ]
            localization_code = TemplateProvider.get_localization_template(root_sheet_name, today_date).format(
                root_sheet_name=root_sheet_name,
                today_date=today_date,
                fields="\n  ".join(localization_fields)
            )
            output_file = os.path.join(self.output_folder, f"languages_{self.class_name.lower()}_{lang.lower()}.dart")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(localization_code)

        # Write the keys file for localization
        for lang, translations in self.localization_data.items():
            localization_fields = [f'String get {key}_ufind_v2;' for key, value in translations.items()]
            localization_code = TemplateProvider.get_localization_template(root_sheet_name, today_date).format(
                root_sheet_name=root_sheet_name,
                today_date=today_date,
                fields="\n  ".join(localization_fields)
            )
            with open(os.path.join(self.output_folder, f"keys.dart"), 'w', encoding='utf-8') as f:
                f.write(localization_code)

        print(f"Dart files generated for class: {self.class_name} in {self.output_folder}")
