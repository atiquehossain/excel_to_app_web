"""
Management command to initialize the project structure.
"""
import os
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Initialize project structure and create necessary directories'

    def handle(self, *args, **options):
        # Create media directory
        media_dir = os.path.join(settings.BASE_DIR, 'media')
        uploads_dir = os.path.join(media_dir, 'uploads')
        os.makedirs(uploads_dir, exist_ok=True)
        self.stdout.write(self.style.SUCCESS(f'Created directory: {uploads_dir}'))

        # Create generated_code directory
        generated_dir = os.path.join(settings.BASE_DIR, settings.DART_SETTINGS['output_folder'])
        os.makedirs(generated_dir, exist_ok=True)
        self.stdout.write(self.style.SUCCESS(f'Created directory: {generated_dir}'))

        # Create templates directory
        templates_dir = os.path.join(settings.BASE_DIR, 'templates', 'excel_converter')
        os.makedirs(templates_dir, exist_ok=True)
        self.stdout.write(self.style.SUCCESS(f'Created directory: {templates_dir}'))

        # Create static directory
        static_dir = os.path.join(settings.BASE_DIR, 'static')
        os.makedirs(static_dir, exist_ok=True)
        self.stdout.write(self.style.SUCCESS(f'Created directory: {static_dir}'))

        self.stdout.write(self.style.SUCCESS('Project structure initialized successfully')) 