"""
Views for excel_converter app.
"""
import os
import json
import zipfile
import tempfile
import pandas as pd
import re
from django.shortcuts import render, redirect
from django.http import JsonResponse, FileResponse, HttpResponse, HttpResponseRedirect
from django.views.decorators.http import require_http_methods, require_POST
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .forms import ExcelUploadForm
from .utils import process_excel_file, get_excel_sheets
from .dart_generator import generate_dart_code
from django.urls import reverse
from django.contrib import messages
import traceback

def index(request):
    """Render the main page."""
    form = ExcelUploadForm()
    return render(request, 'excel_converter/index.html', {'form': form})

def docs(request):
    """Render the documentation page."""
    return render(request, 'excel_converter/docs.html')

@swagger_auto_schema(
    method='post',
    operation_description="Get all sheets from an Excel file",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'file': openapi.Schema(type=openapi.TYPE_FILE, description='Excel file to process'),
        },
        required=['file']
    ),
    responses={
        200: openapi.Response(
            description="Success",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'sheets': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING)),
                    'filename': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )
        ),
        400: "Bad Request",
        500: "Server Error"
    }
)
@api_view(['POST'])
def get_sheets(request):
    """Get all sheets from an Excel file."""
    if 'file' not in request.FILES:
        return JsonResponse({'error': 'No file part'}, status=400)
    
    try:
        # Get the uploaded file
        excel_file = request.FILES['file']
        
        # Save the file temporarily
        path = default_storage.save(f'uploads/{excel_file.name}', ContentFile(excel_file.read()))
        full_path = os.path.join(settings.MEDIA_ROOT, path)
        
        try:
            # Get all sheets from the Excel file
            sheets = get_excel_sheets(full_path)
            
            if not sheets:
                return JsonResponse({'error': 'No sheets found in the Excel file'}, status=400)
            
            response_data = {
                'success': True,
                'sheets': sheets,
                'filename': excel_file.name
            }
            return JsonResponse(response_data)
            
        except Exception as e:
            return JsonResponse({'error': f'Error processing Excel file: {e}'}, status=500)
        finally:
            # We don't delete the file here as we'll need it for processing
            pass
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["POST"])
def upload_file(request):
    """Handle file upload and processing."""
    form = ExcelUploadForm(request.POST, request.FILES)
    
    if not form.is_valid():
        return JsonResponse({'error': form.errors}, status=400)
    
    try:
        # Get form data
        class_name = form.cleaned_data['class_name']
        sheets = request.POST.getlist('sheets', [])
        ideal_sheet = request.POST.get('ideal_sheet', '')
        
        # Get column selections
        database_column = request.POST.get('database_column', '')
        question_column = request.POST.get('question_column', '')
        field_name_column = request.POST.get('field_name_column', '')
        datatype_column = request.POST.get('datatype_column', '')
        question_serial_column = request.POST.get('question_serial_column', '')
        
        # Get language support options
        language_support = request.POST.get('language_support', 'no')
        question_languages = []
        field_languages = []
        
        if language_support == 'yes':
            try:
                question_languages = json.loads(request.POST.get('question_languages', '[]'))
                field_languages = json.loads(request.POST.get('field_languages', '[]'))
            except json.JSONDecodeError:
                return JsonResponse({'error': 'Invalid language selection format'}, status=400)
            
            if not question_languages or not field_languages:
                return JsonResponse({'error': 'Please select at least one language for both questions and fields'}, status=400)
        
        if not sheets:
            return JsonResponse({'error': 'No sheets selected'}, status=400)
        
        if not ideal_sheet:
            ideal_sheet = sheets[0]  # Use the first selected sheet as the ideal sheet if not specified
        
        # Validate required columns
        required_columns = {
            'database_column': database_column,
            'question_column': question_column,
            'field_name_column': field_name_column,
            'datatype_column': datatype_column,
            'question_serial_column': question_serial_column
        }
        
        missing_columns = [k for k, v in required_columns.items() if not v]
        if missing_columns:
            return JsonResponse({'error': f'Missing required columns: {", ".join(missing_columns)}'}, status=400)
        
        # Check if we're using a previously uploaded file
        filename = request.POST.get('filename', '')
        if filename:
            path = f'uploads/{filename}'
            if not default_storage.exists(path):
                return JsonResponse({'error': 'File not found'}, status=400)
        else:
            # Get the uploaded file
            excel_file = request.FILES['file']
            # Save the file
            path = default_storage.save(f'uploads/{excel_file.name}', ContentFile(excel_file.read()))
        
        try:
            # Process the Excel file for each selected sheet
            generated_files = []
            
            # Process the ideal sheet first
            ideal_df = process_excel_file(path, ideal_sheet)
            
            # Add column information to metadata
            metadata = {
                'database_column': database_column,
                'question_column': question_column,
                'field_name_column': field_name_column,
                'datatype_column': datatype_column,
                'question_serial_column': question_serial_column,
                'ideal_sheet': ideal_sheet,
                'language_support': language_support,
                'question_languages': question_languages,
                'field_languages': field_languages
            }
            
            ideal_output_file = generate_dart_code(ideal_df, class_name, preview=False, metadata=metadata)
            generated_files.append(ideal_output_file)
            
            # Process other selected sheets
            for sheet in sheets:
                if sheet != ideal_sheet:  # Skip the ideal sheet as it's already processed
                    df = process_excel_file(path, sheet)
                    sheet_class_name = f"{class_name}_{sheet.replace(' ', '_')}"
                    output_file = generate_dart_code(df, sheet_class_name, preview=False, metadata=metadata)
                    generated_files.append(output_file)
            
            # Read the generated code from the ideal sheet
            with open(ideal_output_file, 'r', encoding='utf-8') as f:
                generated_code = f.read()
            
            return JsonResponse({
                'success': True,
                'code': generated_code,
                'message': f'Code generated successfully for {len(sheets)} sheets',
                'files': [os.path.basename(f) for f in generated_files]
            })
            
        finally:
            # Clean up the uploaded file
            if default_storage.exists(path):
                default_storage.delete(path)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
def preview_code(request):
    """Preview the generated code."""
    try:
        # Get generation results from session
        results = request.session.get('generation_results', {})
        if not results:
            messages.error(request, 'No generation results found')
            return redirect('excel_converter:app_builder')
        
        app_name = results.get('app_name', '')
        generated_files = results.get('generated_files', [])
        
        # Get sheets from session
        sheets = request.session.get('selected_sheets', [])
        ideal_sheet = request.session.get('ideal_sheet', '')
        
        if not sheets or not ideal_sheet:
            messages.error(request, 'Session data missing')
            return redirect('excel_converter:index')
        
        # Create context for preview template
        context = {
            'app_name': app_name,
            'generated_files': generated_files,
            'sheets': sheets,
            'ideal_sheet': ideal_sheet,
            'preview_code': True  # Flag to indicate preview mode
        }
        
        return render(request, 'excel_converter/preview.html', context)
        
    except Exception as e:
        messages.error(request, f'Error generating preview: {str(e)}')
        return redirect('excel_converter:app_builder')

def download_file(request, filename):
    """Download the generated Dart file."""
    try:
        file_path = os.path.join(settings.DART_SETTINGS['output_folder'], filename)
        if not os.path.exists(file_path):
            return JsonResponse({'error': f'File not found: {filename}'}, status=404)
            
        return FileResponse(
            open(file_path, 'rb'),
            as_attachment=True,
            filename=filename
        )
    except Exception as e:
        print(f"Error in download_file view: {e}")
        return JsonResponse({'error': str(e)}, status=404)

def download_all_files(request):
    """Download all generated Dart files as a zip archive."""
    try:
        # Get the list of files from the request
        files_json = request.GET.get('files', '[]')
        files = json.loads(files_json)
        
        if not files:
            return JsonResponse({'error': 'No files specified'}, status=400)
        
        # Create a temporary zip file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
            temp_path = temp_file.name
        
        # Create the zip file
        with zipfile.ZipFile(temp_path, 'w') as zip_file:
            for filename in files:
                file_path = os.path.join(settings.DART_SETTINGS['output_folder'], filename)
                if os.path.exists(file_path):
                    zip_file.write(file_path, filename)
        
        # Return the zip file
        response = FileResponse(
            open(temp_path, 'rb'),
            as_attachment=True,
            filename='dart_files.zip'
        )
        
        # Set the Content-Disposition header to force download
        response['Content-Disposition'] = 'attachment; filename="dart_files.zip"'
        
        return response
    
    except Exception as e:
        print(f"Error in download_all_files view: {e}")
        return JsonResponse({'error': str(e)}, status=500)

def normalize_column_name(column):
    """Normalize column names by removing special characters, spaces and converting to lowercase."""
    # Convert to string in case it's a number
    column = str(column)
    # Remove spaces and convert to lowercase
    normalized = column.lower().replace(' ', '')
    # Replace special characters with empty string
    normalized = re.sub(r'[^a-z0-9]', '', normalized)
    return normalized

def validate_row_data(df, required_columns):
    """Validate each row has required data."""
    validation_results = {
        'valid_rows': [],
        'invalid_rows': []
    }
    
    # Create a mapping of normalized column names to actual column names
    column_mapping = {}
    for col in df.columns:
        norm_col = normalize_column_name(col)
        column_mapping[norm_col] = col
    
    # Find matching columns for each required column
    matched_columns = {}
    for req_col in required_columns:
        norm_req = normalize_column_name(req_col)
        if norm_req in column_mapping:
            matched_columns[req_col] = column_mapping[norm_req]
        else:
            matched_columns[req_col] = None
    
    # Find the English question column
    question_col = None
    for col in df.columns:
        if normalize_column_name(col) in ['questionsinenglish', 'questioninengish', 'englishquestion']:
            question_col = col
            break
    
    for index, row in df.iterrows():
        row_number = index + 2  # Adding 2 because Excel rows start at 1 and we have headers
        missing_fields = []
        
        # Skip empty rows
        if row.isna().all():
            continue
        
        # Check if row has any meaningful data
        has_data = False
        for col in df.columns:
            value = str(row[col]).strip()
            if value and value.lower() != 'nan':
                has_data = True
                break
                
        if not has_data:
            continue
        
        # Skip validation if English question is empty
        if question_col and (pd.isna(row[question_col]) or str(row[question_col]).strip() == '' or str(row[question_col]).lower() == 'nan'):
            continue
        
        # Check each required column including language columns
        for req_col in required_columns:
            actual_col = matched_columns.get(req_col)
            if actual_col and actual_col in df.columns:
                value = str(row[actual_col]).strip()
                # For language columns, only validate if the English question exists
                if ('Questions in' in req_col or 'Field Names in' in req_col):
                    if has_data and question_col and not pd.isna(row[question_col]):
                        if pd.isna(value) or value == '' or value.lower() == 'nan':
                            missing_fields.append(req_col)
                else:
                    # For non-language columns, validate normally
                    if pd.isna(value) or value == '' or value.lower() == 'nan':
                        if has_data:
                            missing_fields.append(req_col)
            else:
                if has_data:
                    missing_fields.append(req_col)
        
        if missing_fields:
            validation_results['invalid_rows'].append({
                'row_number': row_number,
                'missing_fields': missing_fields
            })
        else:
            validation_results['valid_rows'].append(row_number)
    
    return validation_results

@swagger_auto_schema(
    method='post',
    operation_description="Validate selected columns in sheets",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'filename': openapi.Schema(type=openapi.TYPE_STRING),
            'sheets': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING)),
            'columns': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING)),
        },
        required=['filename', 'sheets', 'columns']
    ),
    responses={
        200: "Validation results page",
        400: "Bad Request",
        500: "Server Error"
    }
)
@api_view(['POST'])
def validate_columns(request):
    try:
        print("\n=== Validation Data ===")
        print("Request data:", request.data)
        # Get form data
        filename = request.POST.get('filename')
        sheets = json.loads(request.POST.get('sheets', '[]'))
        columns_to_check = json.loads(request.POST.get('columns', '[]'))
        
        # Validate that we have at least one sheet
        if not sheets:
            return JsonResponse({'error': 'Please select at least one sheet'}, status=400)
        
        # Get ideal sheet, default to the first sheet if not specified
        ideal_sheet = request.POST.get('ideal_sheet')
        if not ideal_sheet:
            ideal_sheet = sheets[0]
        
        # Validate ideal sheet is in selected sheets
        if ideal_sheet not in sheets:
            return JsonResponse({'error': 'Ideal sheet must be one of the selected sheets'}, status=400)
        
        # Get column selections
        database_column = request.POST.get('database_column', '')
        question_column = request.POST.get('question_column', '')
        field_name_column = request.POST.get('field_name_column', '')
        datatype_column = request.POST.get('datatype_column', '')
        question_serial_column = request.POST.get('question_serial_column', '')
        
        # Get language support options
        language_support = request.POST.get('language_support', 'no')
        question_languages = []
        field_languages = []
        
        if language_support == 'yes':
            try:
                question_languages = json.loads(request.POST.get('question_languages', '[]'))
                field_languages = json.loads(request.POST.get('field_languages', '[]'))
            except json.JSONDecodeError:
                return JsonResponse({'error': 'Invalid language selection format'}, status=400)
        
        # Required columns for row validation
        required_row_columns = [
            database_column,
            question_column,
            datatype_column,
            question_serial_column
        ]
        
        # Add language columns to required columns if language support is enabled
        if language_support == 'yes':
            # Add question language columns
            for lang in question_languages:
                if lang.lower() != 'english':  # English is already in required columns
                    # Remove duplicate "Questions in" prefix if it exists
                    lang = lang.replace('Questions in ', '')
                    required_row_columns.append(f'Questions in {lang}')
            
            # Add field language columns
            for lang in field_languages:
                if lang.lower() != 'english':  # English is already in required columns
                    # Remove duplicate "Field Names in " prefix if it exists
                    lang = lang.replace('Field Names in ', '')
                    required_row_columns.append(f'Field Names in {lang}')
        
        # Initialize validation results
        result = {
            'column_validation': {},
            'row_validation': {}
        }
        
        for sheet in sheets:
            # Process the Excel file for each sheet
            df = process_excel_file(filename, sheet)
            
            # Remove completely empty rows
            df = df.dropna(how='all')
            
            # Create normalized column mapping
            column_mapping = {}
            for col in df.columns:
                norm_col = normalize_column_name(col)
                column_mapping[norm_col] = col
            
            # Validate columns exist in sheet (using normalized names)
            missing_columns = []
            present_columns = []
            
            # Check base required columns
            columns_to_validate = columns_to_check.copy()
            
            # Add language columns to validation if language support is enabled
            if language_support == 'yes':
                for lang in question_languages:
                    if lang.lower() != 'english':
                        # Remove duplicate "Questions in" prefix if it exists
                        lang = lang.replace('Questions in ', '')
                        columns_to_validate.append(f'Questions in {lang}')
                
                for lang in field_languages:
                    if lang.lower() != 'english':
                        # Remove duplicate "Field Names in " prefix if it exists
                        lang = lang.replace('Field Names in ', '')
                        columns_to_validate.append(f'Field Names in {lang}')
            
            for col in columns_to_validate:
                norm_col = normalize_column_name(col)
                if norm_col in column_mapping:
                    present_columns.append(col)
                else:
                    missing_columns.append(col)
            
            result['column_validation'][sheet] = {
                'missing': missing_columns,
                'present': present_columns
            }
            
            # Validate row data including language columns
            row_validation = validate_row_data(df, required_row_columns)
            result['row_validation'][sheet] = row_validation
        
        # Check if there are any validation issues
        has_column_issues = any(
            result['column_validation'].get(sheet, {}).get('missing', [])
            for sheet in sheets
        )
        
        has_row_issues = any(
            len(result['row_validation'].get(sheet, {}).get('invalid_rows', [])) > 0
            for sheet in sheets
        )
        
        try:
            # Store data in session
            request.session['selected_sheets'] = sheets
            request.session['ideal_sheet'] = ideal_sheet
            request.session['filename'] = filename
            request.session['metadata'] = {
                'database_column': database_column,
                'question_column': question_column,
                'field_name_column': field_name_column,
                'datatype_column': datatype_column,
                'question_serial_column': question_serial_column,
                'ideal_sheet': ideal_sheet,
                'language_support': language_support,
                'question_languages': question_languages,
                'field_languages': field_languages
            }
            
            print("\n=== Storing Metadata ===")
            print("Field name column:", field_name_column)
            print("Full metadata:", request.session['metadata'])
            
            if not has_column_issues and not has_row_issues:
                # Store all necessary data in session
                request.session['selected_sheets'] = sheets
                request.session['ideal_sheet'] = ideal_sheet
                request.session['filename'] = filename
                request.session['metadata'] = {
                    'database_column': database_column,
                    'question_column': question_column,
                    'field_name_column': field_name_column,
                    'datatype_column': datatype_column,
                    'question_serial_column': question_serial_column,
                    'ideal_sheet': ideal_sheet,
                    'language_support': language_support,
                    'question_languages': question_languages,
                    'field_languages': field_languages
                }
                
                # Redirect to app builder
                return HttpResponseRedirect(reverse('excel_converter:app_builder'))
            
            # If there are issues, show validation results
            context = {
                'sheets': sheets,
                'ideal_sheet': ideal_sheet,
                'database_column': database_column,
                'question_column': question_column,
                'field_name_column': field_name_column,
                'datatype_column': datatype_column,
                'question_serial_column': question_serial_column,
                'language_support': language_support,
                'question_languages': question_languages,
                'field_languages': field_languages,
                'validation_result': result,
                'has_issues': has_column_issues or has_row_issues
            }
            
            return render(request, 'excel_converter/validation_results.html', context)
        
        except Exception as e:
            print(f"Error in validate_columns: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    except Exception as e:
        print(f"Error in validate_columns: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@swagger_auto_schema(
    method='post',
    operation_description="Get column headers from a sheet",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'filename': openapi.Schema(type=openapi.TYPE_STRING),
            'sheet_name': openapi.Schema(type=openapi.TYPE_STRING),
        },
        required=['filename', 'sheet_name']
    ),
    responses={
        200: openapi.Response(
            description="Success",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'columns': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'original': openapi.Schema(type=openapi.TYPE_STRING),
                                'normalized': openapi.Schema(type=openapi.TYPE_STRING),
                            }
                        )
                    ),
                    'normalized_map': openapi.Schema(type=openapi.TYPE_OBJECT),
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )
        ),
        400: "Bad Request",
        500: "Server Error"
    }
)
@api_view(['POST'])
def get_columns(request):
    """Get column headers from a sheet."""
    try:
        filename = request.POST.get('filename', '')
        sheet_name = request.POST.get('sheet_name', '')
        
        if not filename or not sheet_name:
            return JsonResponse({'error': 'Filename and sheet name are required'}, status=400)
        
        path = f'uploads/{filename}'
        if not default_storage.exists(path):
            return JsonResponse({'error': 'File not found'}, status=400)
        
        try:
            full_path = os.path.join(settings.MEDIA_ROOT, path)
            df = pd.read_excel(full_path, sheet_name=sheet_name)
            
            # Create a mapping of normalized names to original names
            normalized_map = {normalize_column_name(col): col for col in df.columns}
            
            # Get both original and normalized columns
            columns = [{
                'original': col,
                'normalized': normalize_column_name(col)
            } for col in df.columns]
            
            return JsonResponse({
                'success': True,
                'columns': columns,
                'normalized_map': normalized_map,
                'message': f'Retrieved {len(columns)} columns from {sheet_name}'
            })
            
        except Exception as e:
            print(f"Error processing Excel file: {e}")
            return JsonResponse({'error': f'Error processing Excel file: {e}'}, status=500)
    
    except Exception as e:
        print(f"Error in get_columns view: {e}")
        return JsonResponse({'error': str(e)}, status=500)

def app_builder(request):
    """Render the app builder setup page."""
    # Get sheets from session if available
    sheets = request.session.get('selected_sheets', [])
    ideal_sheet = request.session.get('ideal_sheet', '')
    
    if not sheets:
        # If no sheets in session, redirect back to index
        messages.error(request, 'Please select sheets first')
        return redirect('excel_converter:index')
    
    # Ensure ideal_sheet is set
    if not ideal_sheet and sheets:
        ideal_sheet = sheets[0]
    
    context = {
        'sheets': sheets,
        'ideal_sheet': ideal_sheet
    }
    return render(request, 'excel_converter/app_builder.html', context)

@require_http_methods(["POST"])
def generate_database(request):
    """Generate database for each sheet with custom class names."""
    try:
        # Debug prints for metadata
        print("\n=== DEBUG METADATA ===")
        metadata = request.session.get('metadata', {})
        print("All metadata:", metadata)
        print("Field name column from metadata:", metadata.get('field_name_column'))
        print("Available columns in metadata:", list(metadata.keys()))
        print("=== END DEBUG ===\n")

        # Get form data
        app_name = request.POST.get('appName')
        if not app_name:
            return JsonResponse({'error': 'App name is required'}, status=400)
        
        # Get sheets and metadata from session
        sheets = request.session.get('selected_sheets', [])
        ideal_sheet = request.session.get('ideal_sheet', '')
        
        if not sheets:
            return JsonResponse({'error': 'No sheets found in session'}, status=400)
        
        # Get the Excel file path from session
        filename = request.session.get('filename')
        if not filename:
            return JsonResponse({'error': 'Excel file not found'}, status=400)
        
        path = f'uploads/{filename}'
        if not default_storage.exists(path):
            return JsonResponse({'error': 'Excel file not found'}, status=400)
        
        # Get metadata from session
        metadata = request.session.get('metadata', {})
        if not metadata:
            return JsonResponse({'error': 'Column metadata not found'}, status=400)
        
        # Get custom class names for each sheet
        sheet_classes = {}
        for sheet in sheets:
            class_name = request.POST.get(f'sheet_class_{sheet}')
            if not class_name:
                return JsonResponse({'error': f'Class name missing for sheet: {sheet}'}, status=400)
            sheet_classes[sheet] = class_name
        
        # Process each sheet
        generated_files = []
        for sheet in sheets:
            df = process_excel_file(path, sheet)
            
            print(f"\n=== Processing Sheet: {sheet} ===")
            print("DataFrame columns:", df.columns.tolist())
            
            # Get questions and fields
            questions = []
            fields = []
            
            # Get column names from metadata
            question_col = metadata.get('question_column', '')
            field_name_col = metadata.get('field_name_column', '')
            
            print(f"Looking for question column: '{question_col}'")
            print(f"Looking for field name column: '{field_name_col}'")
            
            # Try different variations of column names
            question_variations = [
                question_col,
                'Questions in English',
                'questions_in_english',
                'Questions',
                'Question',
                'Question no.',
                'question_no',
                'question_number',
                'q_no',
                'qno',
            ]
            
            field_variations = [
                field_name_col,
                'Field Names in English',
                'field_names_in_english',
                'Field Names',
                'Fields',
                'Labels in English',  # Add common variations
                'labels_in_english',
                'Label',
                'Labels',
                'Field Label',
                'Field Labels'
            ]
            
            # Find question column
            actual_question_col = None
            for possible_col in question_variations:
                for col in df.columns:
                    if col.lower().strip() == possible_col.lower().strip():
                        actual_question_col = col
                        print(f"Found matching question column: '{col}'")
                        break
                if actual_question_col:
                    break
            
            # Find field name column
            actual_field_col = None
            for possible_col in field_variations:
                if possible_col:  # Only check if possible_col is not empty
                    print(f"Checking for field column: '{possible_col}'")
                    for col in df.columns:
                        print(f"  Comparing with: '{col}'")
                        if col.lower().strip() == possible_col.lower().strip():
                            actual_field_col = col
                            print(f"Found matching field column: '{col}'")
                            break
                if actual_field_col:
                    break
            
            if not actual_field_col:
                print("Available columns for field names:")
                for col in df.columns:
                    print(f"  - {col}")
            
            # Process questions
            if actual_question_col:
                print(f"Processing questions from column: '{actual_question_col}'")
                database_col = metadata.get('database_column', '').lower().strip()
                datatype_col = metadata.get('datatype_column', '').lower().strip()
                
                print(f"Datatype column from metadata: '{datatype_col}'")
                print(f"All columns: {df.columns.tolist()}")
                
                # Print the first few rows of the dataframe to see what's in it
                print("\nFirst 3 rows of the dataframe:")
                for idx, row in df.head(3).iterrows():
                    print(f"\nRow {idx}:")
                    for col in df.columns:
                        print(f"  {col}: {row.get(col, '')}")
                
                # Try to find the data type column directly
                data_type_col = None
                data_type_variations = ['Data type', 'data type', 'datatype', 'Data Type', 'field type', 'Field Type', 'type']
                
                for variation in data_type_variations:
                    for col in df.columns:
                        if variation.lower() in col.lower():
                            data_type_col = col
                            print(f"Found data type column: '{col}' (matched with '{variation}')")
                            break
                    if data_type_col:
                        break
                
                if data_type_col:
                    print(f"Using data type column: '{data_type_col}' instead of '{datatype_col}'")
                    datatype_col = data_type_col
                
                # Look specifically for question number column
                question_no_col = None
                question_no_variations = ['Question no.', 'question_no', 'question_number', 'q_no', 'qno', 'sl', 'sl.no', 'serial']
                
                for possible_col in question_no_variations:
                    for col in df.columns:
                        if col.lower().strip() == possible_col.lower().strip():
                            question_no_col = col
                            print(f"Found question number column: '{col}'")
                            break
                    if question_no_col:
                        break
                
                # Hardcoded field types for specific questions
                hardcoded_types = {
                    'natural_disasters_affected': 'Multiple Choice',
                    'latitude': 'Text',
                    'longitude': 'Text',
                    'lost_income_6_month': 'Dropdown',
                    'income_lost': 'Multiple Choice',
                    'loss_of_livelihood': 'Dropdown',
                    'loss_of_livelihood_type': 'Multiple Choice'
                }
                
                # For each row, print detailed debugging info
                for idx, row in df.iterrows():
                    question = row.get(actual_question_col, '')
                    database_value = row.get(database_col, '')
                    
                    print(f"\nProcessing row {idx}, question: '{question}', database: '{database_value}'")
                    
                    # Get field type with multiple fallbacks
                    field_type = "Text"  # Default
                    
                    # Try to get from datatype column
                    if datatype_col and datatype_col in df.columns:
                        raw_field_type = row.get(datatype_col, '')
                        print(f"  Raw field type from column '{datatype_col}': '{raw_field_type}'")
                        if pd.notna(raw_field_type) and str(raw_field_type).strip():
                            field_type = str(raw_field_type).strip()
                            print(f"  Using field type from column: '{field_type}'")
                    else:
                        print(f"  Datatype column '{datatype_col}' not found in {df.columns.tolist()}")
                    
                    # Check hardcoded types based on database value
                    if database_value and database_value.lower() in hardcoded_types:
                        old_field_type = field_type
                        field_type = hardcoded_types[database_value.lower()]
                        print(f"  Overriding field type '{old_field_type}' with hardcoded type '{field_type}' for '{database_value}'")
                    
                    # After getting the field type
                    # Get question number from the dedicated column if available
                    question_no = idx + 1  # Default to row index + 1
                    if question_no_col and question_no_col in df.columns:
                        q_no_value = row.get(question_no_col, '')
                        if pd.notna(q_no_value) and str(q_no_value).strip():
                            question_no = str(q_no_value).strip()
                            print(f"  Found question number: {question_no} for question: {question}")
                    
                    # Final field type
                    print(f"  Final field type: '{field_type}'")
                    
                    if pd.notna(question) and str(question).strip():
                        question_text = str(question).strip()
                        
                        # If we have a database value, use it as prefix for the key
                        if pd.notna(database_value) and str(database_value).strip():
                            # Convert database value to key format
                            db_key = str(database_value).strip().lower()
                            db_key = re.sub(r'[^a-z0-9]+', '_', db_key)
                            db_key = re.sub(r'_+', '_', db_key)
                            db_key = db_key.strip('_')
                            
                            # Add model name as suffix
                            model_name = sheet_classes[sheet].lower()
                            key = f"{db_key}_{model_name}"
                        else:
                            # If no database value, use the question text
                            key = question_text.lower()
                            key = re.sub(r'[^a-z0-9]+', '_', key)
                            key = re.sub(r'_+', '_', key)
                            key = key.strip('_')
                            # Add model name as suffix
                            model_name = sheet_classes[sheet].lower()
                            key = f"{key}_{model_name}"
                        
                        if not any(q['key'] == key for q in questions):
                            questions.append({
                                'question': question_text,
                                'key': key,
                                'database': database_value,
                                'field_type': field_type,
                                'question_no': question_no
                            })
                            print(f"Added question: '{question_text}' with key: '{key}', field_type: '{field_type}'")
            
            # Process field names
            if actual_field_col:
                print(f"Processing fields from column: '{actual_field_col}'")
                database_col = metadata.get('database_column', '').lower().strip()
                
                # Keep track of the current database context
                current_database_value = None
                
                for _, row in df.iterrows():
                    field = row[actual_field_col]
                    database_value = row.get(database_col, '')
                    
                    # Update current database context if we have a new database value
                    if pd.notna(database_value) and str(database_value).strip():
                        current_database_value = str(database_value).strip()
                        print(f"Updated database context to: {current_database_value}")
                    
                    if pd.notna(field) and str(field).strip():
                        field_text = str(field).strip()
                        
                        # Convert field value to key format
                        field_key = sanitize_key(field_text)
                        
                        # Generate key based on context
                        if current_database_value:
                            # Convert database value to key format
                            db_key = sanitize_key(current_database_value)
                            
                            # Combine: fieldkey_databasevalue (e.g., farming_income_lost)
                            key = f"{field_key}_{db_key}"
                            
                            print(f"Generated key with database context: {key}")
                        else:
                            # No database context, use simple format
                            key = field_key
                            print(f"Generated key without database context: {key}")
                        
                        # Don't add model name to the key
                        if not any(f['key'] == key for f in fields):
                            fields.append({
                                'field': field_text,
                                'key': key,
                                'database_value': current_database_value
                            })
                            print(f"Added field: '{field_text}' with key: '{key}' (database: {current_database_value})")
            
            # Generate code for the sheet
            code = generate_dart_code(df, sheet_classes[sheet], preview=True, metadata=metadata)
            
            generated_files.append({
                'sheet': sheet,
                'class_name': sheet_classes[sheet],
                'status': 'success',
                'generated_code': code,
                'questions': questions,
                'fields': fields
            })
        
        # Print final results
        print("\nFinal Results:")
        for file in generated_files:
            print(f"\nSheet: {file['sheet']}")
            print(f"Questions found: {len(file['questions'])}")
            print(f"Fields found: {len(file['fields'])}")
            
        # Store results in session
        request.session['generation_results'] = {
            'app_name': app_name,
            'generated_files': generated_files
        }
        
        return JsonResponse({
            'success': True,
            'redirect_url': reverse('excel_converter:generation_results')
        })
        
    except Exception as e:
        print(f"Error in generate_database: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

def generation_results(request):
    """Show the results of database generation."""
    # Get results from session
    results = request.session.get('generation_results', {})
    if not results:
        messages.error(request, 'No generation results found')
        return redirect('excel_converter:app_builder')
    
    context = {
        'app_name': results.get('app_name', ''),
        'generated_files': results.get('generated_files', [])
    }
    return render(request, 'excel_converter/generation_results.html', context)

def sanitize_key(name):
    """Sanitize keys to ensure they are valid Dart identifiers."""
    # Convert to lowercase and strip whitespace
    key = str(name).strip().lower()
    # Replace non-alphanumeric characters with underscore
    key = re.sub(r'[^0-9a-zA-Z]+', '_', key)
    # Remove multiple underscores
    key = re.sub(r'_+', '_', key)
    # Remove leading/trailing underscores
    return key.strip('_') 