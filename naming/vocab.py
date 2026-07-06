"""
Vocabulary loader — reads ``vocabulary.yaml`` and provides typed helpers
for building dropdown choices on the name-generator page.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

#: Absolute path to the vocabulary YAML shipped with the app.
VOCAB_PATH: Path = Path(__file__).resolve().parent / "vocabulary.yaml"

# Type aliases for readability
VocabDict = dict[str, Any]
ChoiceList = list[tuple[str, str]]
GroupedChoices = list[tuple[str, ChoiceList]]
TagSuggestions = dict[str, list[str]]


def _load_raw(path: Path | None = None) -> VocabDict:
    """Load the raw YAML file.

    Not cached so every request always sees fresh data after an edit.

    Args:
        path: Override path for testing. Falls back to :data:`VOCAB_PATH`.
    """
    target = path or VOCAB_PATH
    with open(target) as fh:
        data: VocabDict = yaml.safe_load(fh)
    return data


def save_vocab(data: VocabDict, path: Path | None = None) -> None:
    """Write *data* back to the vocabulary YAML file.

    Args:
        data: Full vocabulary dictionary to persist.
        path: Override path for testing. Falls back to :data:`VOCAB_PATH`.
    """
    target = path or VOCAB_PATH
    with open(target, "w") as fh:
        yaml.dump(data, fh, default_flow_style=False, sort_keys=False, allow_unicode=True)


def get_vocab(path: Path | None = None) -> VocabDict:
    """Return the full vocabulary dict.

    Args:
        path: Override path for testing.
    """
    return _load_raw(path)


def get_choices(field_name: str, path: Path | None = None) -> ChoiceList:
    """Return ``(code, label)`` tuples for a flat vocabulary field.

    Handles both flat dicts (owner, provider, …) and nested dicts
    (purpose) by flattening the latter with a category suffix.

    Args:
        field_name: Top-level key in vocabulary.yaml (e.g. ``"owner"``).
        path: Override path for testing.
    """
    data = _load_raw(path)
    field_data: Any = data.get(field_name, {})

    if isinstance(field_data, dict):
        first_val = next(iter(field_data.values()), None)
        if isinstance(first_val, dict):
            # Nested — flatten with category label
            choices: ChoiceList = []
            for category, items in field_data.items():
                for code, label in items.items():
                    choices.append((code, f"{label} ({category})"))
            return choices
        return [(code, label) for code, label in field_data.items()]

    return []


def get_purpose_choices(path: Path | None = None) -> GroupedChoices:
    """Return purpose choices grouped by category.

    Returns:
        A list of ``(category_name, [(code, label), …])`` tuples
        suitable for Django's ``<optgroup>`` rendering.

    Args:
        path: Override path for testing.
    """
    data = _load_raw(path)
    purpose_data: dict[str, dict[str, str]] = data.get("purpose", {})
    grouped: GroupedChoices = []
    for category, items in purpose_data.items():
        category_label = category.replace("_", " ").title()
        choices: ChoiceList = [(code, label) for code, label in items.items()]
        grouped.append((category_label, choices))
    return grouped


def get_purpose_flat(path: Path | None = None) -> ChoiceList:
    """Return a flat ``(code, label)`` list for all purposes.

    Args:
        path: Override path for testing.
    """
    data = _load_raw(path)
    purpose_data: dict[str, dict[str, str]] = data.get("purpose", {})
    choices: ChoiceList = []
    for _category, items in purpose_data.items():
        for code, label in items.items():
            choices.append((code, label))
    return choices


def get_tag_suggestions(path: Path | None = None) -> TagSuggestions:
    """Return tag-key suggestions grouped by category.

    Args:
        path: Override path for testing.
    """
    data = _load_raw(path)
    return data.get("tags", {})  # type: ignore[no-any-return]
