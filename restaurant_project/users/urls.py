from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.custom_login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
]

