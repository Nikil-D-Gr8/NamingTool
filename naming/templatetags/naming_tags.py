"""Custom template tags and filters for the *naming* app."""

from __future__ import annotations

from typing import Any

from django import template

register = template.Library()


@register.filter
def get_field(vocab_dict: dict[str, Any], field_name: str) -> Any:
    """Look up *field_name* in the vocabulary dict.

    Usage in templates::

        {% load naming_tags %}
        {{ vocab|get_field:"owner" }}
    """
    return vocab_dict.get(field_name, {})
