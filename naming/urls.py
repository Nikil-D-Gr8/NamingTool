"""URL routing for the *naming* app."""

from __future__ import annotations

from django.urls import URLPattern, path

from . import views

urlpatterns: list[URLPattern] = [
    path("", views.home, name="home"),
    path("vocabulary/", views.vocabulary_manage, name="vocabulary_manage"),
]
