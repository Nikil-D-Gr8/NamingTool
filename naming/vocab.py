"""
Vocabulary loader — reads vocabulary.yaml and provides choices for forms.
"""

import os
import yaml
from functools import lru_cache
from pathlib import Path

VOCAB_PATH = Path(__file__).resolve().parent / "vocabulary.yaml"


def _load_raw():
    """Load the raw YAML file. Not cached so we always get fresh data."""
    with open(VOCAB_PATH, "r") as f:
        return yaml.safe_load(f)


def save_vocab(data):
    """Write updated vocabulary back to the YAML file."""
    with open(VOCAB_PATH, "w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)


def get_vocab():
    """Return the full vocabulary dict."""
    return _load_raw()


def get_choices(field_name):
    """
    Return a list of (code, label) tuples for a flat field
    (owner, provider, environment, resource_type).
    """
    data = _load_raw()
    field_data = data.get(field_name, {})
    if isinstance(field_data, dict):
        # Check if it's a nested dict (like purpose) or flat
        first_val = next(iter(field_data.values()), None)
        if isinstance(first_val, dict):
            # Nested — flatten
            choices = []
            for category, items in field_data.items():
                for code, label in items.items():
                    choices.append((code, f"{label} ({category})"))
            return choices
        else:
            return [(code, label) for code, label in field_data.items()]
    return []


def get_purpose_choices():
    """
    Return purpose choices grouped by category.
    Returns: list of (category_name, [(code, label), ...])
    """
    data = _load_raw()
    purpose_data = data.get("purpose", {})
    grouped = []
    for category, items in purpose_data.items():
        category_label = category.replace("_", " ").title()
        choices = [(code, label) for code, label in items.items()]
        grouped.append((category_label, choices))
    return grouped


def get_purpose_flat():
    """Return a flat list of (code, label) for purpose."""
    data = _load_raw()
    purpose_data = data.get("purpose", {})
    choices = []
    for category, items in purpose_data.items():
        for code, label in items.items():
            choices.append((code, label))
    return choices


def get_tag_suggestions():
    """Return tag key suggestions grouped by category."""
    data = _load_raw()
    return data.get("tags", {})
