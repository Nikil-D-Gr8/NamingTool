"""Tests for :mod:`naming.templatetags.naming_tags`."""

from __future__ import annotations

from typing import Any

from naming.templatetags.naming_tags import get_field


class TestGetFieldFilter:
    """Tests for the ``get_field`` template filter."""

    def test_returns_value_for_existing_key(self) -> None:
        vocab: dict[str, Any] = {"owner": {"nik": "Nikil"}}
        result = get_field(vocab, "owner")
        assert result == {"nik": "Nikil"}

    def test_returns_empty_dict_for_missing_key(self) -> None:
        vocab: dict[str, Any] = {"owner": {"nik": "Nikil"}}
        result = get_field(vocab, "nonexistent")
        assert result == {}

    def test_returns_empty_dict_for_empty_vocab(self) -> None:
        result = get_field({}, "anything")
        assert result == {}

    def test_works_with_nested_values(self) -> None:
        vocab: dict[str, Any] = {
            "purpose": {
                "infra": {"core": "Core"},
                "apps": {"blog": "Blog"},
            }
        }
        result = get_field(vocab, "purpose")
        assert "infra" in result
        assert result["infra"]["core"] == "Core"

    def test_works_with_list_values(self) -> None:
        vocab: dict[str, Any] = {"tags": {"ownership": ["owner", "team"]}}
        result = get_field(vocab, "tags")
        assert result["ownership"] == ["owner", "team"]
