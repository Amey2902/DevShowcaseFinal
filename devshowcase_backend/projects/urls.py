from django.urls import path
from . import views

urlpatterns = [
    path('projects/', views.project_list, name='project-list'),
    path('projects/create/', views.project_create, name='project-create'),
    path('projects/<slug:slug>/', views.project_detail, name='project-detail'),
    path('projects/<slug:slug>/full/', views.project_full, name='project-full'),
    path('projects/<slug:slug>/update/', views.project_update, name='project-update'),
    path('projects/<slug:slug>/delete/', views.project_delete, name='project-delete'),
    path('techstack/', views.techstack_create, name='techstack-create'),
    path('architecture/', views.architecture_create, name='architecture-create'),
    path('endpoints/', views.endpoint_create, name='endpoint-create'),
    path('endpoints/<int:endpoint_id>/delete/', views.endpoint_delete, name='endpoint-delete'),
    path('projects/<slug:slug>/explain/', views.project_explain, name='project-explain'),
    path('projects/search/ai/', views.project_search_ai, name='project-search-ai'),
    path('timeline/', views.timeline_create, name='timeline-create'),
    
    # Auto-Endpoint Detection URLs
    path('projects/<int:project_id>/upload/files/', views.upload_files, name='upload-files'),
    path('projects/<int:project_id>/upload/zip/', views.upload_zip, name='upload-zip'),
    path('projects/<int:project_id>/upload/github/', views.upload_github, name='upload-github'),
    path('projects/<int:project_id>/translate/', views.translate_api, name='translate-api'),

    path('execute/translated/', views.execute_translated_endpoint, name='execute-translated-endpoint'),
    path('uploads/<uuid:upload_id>/status/', views.upload_status, name='upload-status'),
    path('uploads/<uuid:upload_id>/retry/', views.upload_retry, name='upload-retry'),
    path('uploads/<uuid:upload_id>/', views.upload_delete, name='upload-delete'),
]
