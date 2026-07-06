"""Django app configuration for the *naming* app."""

from __future__ import annotations

from django.apps import AppConfig


class NamingConfig(AppConfig):
    """Configuration for the stateless naming & tagging app."""

    name: str = "naming"
    verbose_name: str = "Resource Naming Tool"
    default_auto_field: str = "django.db.models.BigAutoField"
