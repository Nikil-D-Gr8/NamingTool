from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("vocabulary/", views.vocabulary_manage, name="vocabulary_manage"),
]
