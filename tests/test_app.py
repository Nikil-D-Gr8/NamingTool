"""Tests for ``naming.apps`` and the vocabulary YAML schema."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml
from django.apps import apps

from naming.apps import NamingConfig


class TestNamingAppConfig:
    """Tests for the Django app configuration."""

    def test_app_name(self) -> None:
        assert NamingConfig.name == "naming"

    def test_verbose_name(self) -> None:
        assert NamingConfig.verbose_name == "Resource Naming Tool"

    def test_app_is_installed(self) -> None:
        assert apps.is_installed("naming")


class TestVocabularyYAMLSchema:
    """Validate the structure of ``naming/vocabulary.yaml``.

    These tests run against the *real* shipped vocabulary file to catch
    schema regressions before they reach production.
    """

    VOCAB_PATH: Path = Path(__file__).resolve().parent.parent / "naming" / "vocabulary.yaml"

    @pytest.fixture(autouse=True)
    def _load(self) -> None:
        with open(self.VOCAB_PATH) as fh:
            self.vocab: dict[str, Any] = yaml.safe_load(fh)

    def test_top_level_keys_exist(self) -> None:
        expected = {"owner", "provider", "environment", "resource_type", "purpose", "tags"}
        assert expected.issubset(set(self.vocab.keys()))

    def test_flat_fields_are_string_dicts(self) -> None:
        for field in ("owner", "provider", "environment", "resource_type"):
            data = self.vocab[field]
            assert isinstance(data, dict), f"{field} should be a dict"
            for code, label in data.items():
                assert isinstance(code, str), f"{field} code should be str, got {type(code)}"
                assert isinstance(label, str), f"{field} label should be str, got {type(label)}"

    def test_purpose_is_nested_dict(self) -> None:
        purpose = self.vocab["purpose"]
        assert isinstance(purpose, dict)
        for category, items in purpose.items():
            assert isinstance(category, str)
            assert isinstance(items, dict), f"purpose.{category} should be a dict"
            for code, label in items.items():
                assert isinstance(code, str)
                assert isinstance(label, str)

    def test_tags_categories_are_string_lists(self) -> None:
        tags = self.vocab["tags"]
        assert isinstance(tags, dict)
        for category, keys in tags.items():
            assert isinstance(category, str)
            assert isinstance(keys, list), f"tags.{category} should be a list"
            for key in keys:
                assert isinstance(key, str), f"tags.{category} items should be str"

    def test_owner_codes_are_short(self) -> None:
        """Owner codes should be ≤10 characters to fit in the naming format."""
        for code in self.vocab["owner"]:
            assert len(code) <= 10, f"Owner code '{code}' is too long"

    def test_provider_codes_are_short(self) -> None:
        for code in self.vocab["provider"]:
            assert len(code) <= 10, f"Provider code '{code}' is too long"

    def test_no_empty_categories_in_purpose(self) -> None:
        for category, items in self.vocab["purpose"].items():
            assert len(items) > 0, f"Purpose category '{category}' is empty"
