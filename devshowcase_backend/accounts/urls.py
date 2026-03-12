from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('me/', views.me, name='me'),
    path('profile/<str:username>/', views.user_profile, name='user_profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    
    # Magic Link Authentication
    path('magic-link/request/', views.request_magic_link, name='request_magic_link'),
    path('magic-link/verify/', views.verify_magic_link, name='verify_magic_link'),
]
