import pandas as pd
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from datetime import datetime
from .main import process_combined_projects
from .DartCodeGenerator import DartCodeGenerator

class ExcelConverterView:
    """Main view for handling Excel file processing and code generation"""
    
    @csrf_exempt
    @require_http_methods(["POST"])
    def handle_upload(self, request):
        """
        Handle Excel file upload and return available sheets
        """
        try:
            if 'file' not in request.FILES:
                return JsonResponse({'error': 'No file uploaded'}, status=400)
            
            file = request.FILES['file']
            if not file.name.endswith(('.xlsx', '.xls')):
                return JsonResponse({'error': 'Invalid file type. Please upload an Excel file.'}, status=400)
            
            # Save the file temporarily
            upload_dir = os.path.join('media', 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            file_path = os.path.join(upload_dir, file.name)
            
            with open(file_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
            
            # Get sheet names
            df = pd.read_excel(file_path)
            sheets = df.sheet_names
            
            return JsonResponse({
                'success': True,
                'sheets': sheets,
                'message': f'Successfully uploaded {file.name}'
            })
            
        except Exception as e:
            return JsonResponse({
                'error': str(e),
                'message': 'Error processing file'
            }, status=500)

    @csrf_exempt
    @require_http_methods(["POST"])
    def process_sheet(self, request):
        """
        Process selected sheet and generate code
        """
        try:
            data = json.loads(request.body)
            sheet_name = data.get('sheet')
            
            if not sheet_name:
                return JsonResponse({'error': 'No sheet selected'}, status=400)
            
            # Get the latest uploaded file
            upload_dir = os.path.join('media', 'uploads')
            excel_files = [f for f in os.listdir(upload_dir) if f.endswith(('.xlsx', '.xls'))]
            
            if not excel_files:
                return JsonResponse({'error': 'No Excel file found'}, status=400)
            
            latest_file = max(excel_files, key=lambda x: os.path.getctime(os.path.join(upload_dir, x)))
            file_path = os.path.join(upload_dir, latest_file)
            
            # Process the sheet
            process_combined_projects(file_path, sheet_name)
            
            # Get generated files
            generated_files = []
            output_dir = os.path.join('generated_code')
            for file in os.listdir(output_dir):
                if file.endswith('.dart'):
                    generated_files.append({
                        'name': file,
                        'url': f'/download/{file}'
                    })
            
            return JsonResponse({
                'success': True,
                'files': generated_files,
                'message': f'Successfully processed sheet: {sheet_name}'
            })
            
        except Exception as e:
            return JsonResponse({
                'error': str(e),
                'message': 'Error processing sheet'
            }, status=500)

    @require_http_methods(["GET"])
    def download_file(self, request, filename):
        """
        Handle file downloads
        """
        try:
            file_path = os.path.join('generated_code', filename)
            if not os.path.exists(file_path):
                return JsonResponse({'error': 'File not found'}, status=404)
            
            with open(file_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type='application/octet-stream')
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                return response
                
        except Exception as e:
            return JsonResponse({
                'error': str(e),
                'message': 'Error downloading file'
            }, status=500)

    @require_http_methods(["GET"])
    def download_all(self, request):
        """
        Handle downloading all generated files as a zip
        """
        try:
            import zipfile
            from io import BytesIO
            
            # Create a zip file in memory
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                output_dir = os.path.join('generated_code')
                for file in os.listdir(output_dir):
                    if file.endswith('.dart'):
                        file_path = os.path.join(output_dir, file)
                        zip_file.write(file_path, file)
            
            # Prepare the response
            zip_buffer.seek(0)
            response = HttpResponse(zip_buffer, content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename="generated_code.zip"'
            return response
            
        except Exception as e:
            return JsonResponse({
                'error': str(e),
                'message': 'Error creating zip file'
            }, status=500)

class CodePreviewView:
    """Preview and validation handler"""
    
    def validate_selections(self, request):
        """
        Operation: Selection Validation
        Location: When user clicks "Check Selections" button
        Purpose:
        - Verifies all required fields are selected
        - Checks column data types match
        - Validates language mappings if multilingual
        - Returns validation results to show errors/warnings
        """
        # Checks required selections
        # Validates mappings
        # Returns validation status 