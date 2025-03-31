"""
URL configuration for excel_converter app.
"""
from django.urls import path
from . import views

app_name = 'excel_converter'

urlpatterns = [
    path('', views.homePage, name='index'),
    path('platformPage/', views.platform_page, name='platformPage'),

    path('fromGenerator/', views.fromGenerator, name='fromGenerator'),

    path('docs/', views.docs, name='docs'),
    path('get-sheets/', views.get_sheets, name='get_sheets'),
    path('get-columns/', views.get_columns, name='get_columns'),
    path('validate-columns/', views.validate_columns, name='validate_columns'),
    path('upload/', views.upload_file, name='upload'),
    path('preview/', views.preview_code, name='preview'),
    path('download/<str:filename>/', views.download_file, name='download'),
    path('download-all/', views.download_all_files, name='download_all'),
    path('app-builder/', views.app_builder, name='app_builder'),
    path('generate-database/', views.generate_database, name='generate_database'),
    path('generation-results/', views.generation_results, name='generation_results'),
] 