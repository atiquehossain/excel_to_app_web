# Excel to Dart Code Generator

A powerful tool that converts Excel spreadsheet data into Dart/Flutter code, making it easier to create data models and forms from spreadsheet data.

## Features

- Convert Excel data to Dart/Flutter code
- Support for multiple field types (Dropdown, Multiple choice, Radio, Text, Number, Image)
- Multi-language support (English, Tamil, Sinhala)
- GUI and CLI interfaces
- Customizable templates
- Hidden row handling
- Data type validation

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/excel-mapper.git
cd excel-mapper
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### GUI Version
```bash
python main_gui_version.py
```

### CLI Version
```bash
python main.py --input path/to/excel.xlsx --sheet Sheet1 --output output_folder
```

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