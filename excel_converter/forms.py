"""
Forms for excel_converter app.
"""
from django import forms
from django.conf import settings

class ExcelUploadForm(forms.Form):
    """Form for Excel file upload."""
    file = forms.FileField(
        label='Excel File',
        help_text='Supported formats: .xlsx, .xls, .csv',
        widget=forms.FileInput(attrs={
            'class': 'w-full p-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
            'accept': '.xlsx,.xls,.csv'
        })
    )
    
    class_name = forms.CharField(
        label='Class Name',
        initial='GeneratedClass',
        widget=forms.TextInput(attrs={
            'class': 'w-full p-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
        })
    )
    
    def clean_file(self):
        """Validate the uploaded file."""
        file = self.cleaned_data['file']
        
        # Check file size
        if file.size > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
            raise forms.ValidationError('File size exceeds 16MB limit.')
        
        # Check file extension
        ext = file.name.rsplit('.', 1)[1].lower() if '.' in file.name else ''
        if ext not in ['xlsx', 'xls', 'csv']:
            raise forms.ValidationError('Unsupported file format. Please upload .xlsx, .xls, or .csv files.')
        
        return file
    
    def clean_class_name(self):
        """Validate the class name."""
        class_name = self.cleaned_data['class_name']
        
        # Check if class name is valid
        if not class_name.isidentifier():
            raise forms.ValidationError('Invalid class name. Use only letters, numbers, and underscores.')
        
        return class_name 