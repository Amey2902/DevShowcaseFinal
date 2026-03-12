from django.urls import path
from . import views

urlpatterns = [
    path('generate/<int:project_id>/', views.generate_sandbox, name='generate_sandbox'),
]
