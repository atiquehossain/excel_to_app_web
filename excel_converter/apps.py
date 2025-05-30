"""
Django app configuration for excel_converter.
"""
from django.apps import AppConfig

class ExcelConverterConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'excel_converter'

    def ready(self):
        # This ensures template tags are loaded
        import excel_converter.templatetags.custom_filters 