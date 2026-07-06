"""
URL configuration for NamingTool project.
"""
from django.urls import include, path

urlpatterns = [
    path('', include('naming.urls')),
]
