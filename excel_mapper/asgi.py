"""
ASGI config for excel_mapper project.
"""
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'excel_mapper.settings')
application = get_asgi_application() 