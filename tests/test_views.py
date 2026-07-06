"""Tests for the *naming* app's Django views."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest
from django.test import Client, RequestFactory
from django.urls import reverse

from naming.vocab import get_vocab, save_vocab

# pytest-django needs this
pytestmark = pytest.mark.django_db(databases=[])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
FIXTURE_DIR: Path = Path(__file__).resolve().parent / "fixtures"
TEST_VOCAB_PATH: Path = FIXTURE_DIR / "test_vocabulary.yaml"


def _patch_vocab(tmp_path: Path) -> Path:
    """Copy test vocab to tmp and return the path."""
    dest = tmp_path / "vocabulary.yaml"
    dest.write_text(TEST_VOCAB_PATH.read_text())
    return dest


# ---------------------------------------------------------------------------
# Home view
# ---------------------------------------------------------------------------
class TestHomeView:
    """Tests for the ``home`` view (``/``)."""

    def test_home_returns_200(self, client: Client) -> None:
        response = client.get(reverse("home"))
        assert response.status_code == 200

    def test_home_uses_correct_template(self, client: Client) -> None:
        response = client.get(reverse("home"))
        assert "naming/home.html" in [t.name for t in response.templates]

    def test_home_context_has_choices(self, client: Client) -> None:
        response = client.get(reverse("home"))
        ctx = response.context
        for key in (
            "owner_choices",
            "provider_choices",
            "environment_choices",
            "resource_type_choices",
            "purpose_choices",
            "tag_suggestions",
            "vocab",
        ):
            assert key in ctx, f"Missing context key: {key}"

    def test_home_context_choices_are_lists(self, client: Client) -> None:
        response = client.get(reverse("home"))
        for key in ("owner_choices", "provider_choices", "environment_choices"):
            assert isinstance(response.context[key], list)

    def test_home_contains_preview_element(self, client: Client) -> None:
        response = client.get(reverse("home"))
        content = response.content.decode()
        assert 'id="previewName"' in content

    def test_home_contains_tag_editor(self, client: Client) -> None:
        response = client.get(reverse("home"))
        content = response.content.decode()
        assert 'id="tagsEditor"' in content

    def test_home_contains_copy_buttons(self, client: Client) -> None:
        response = client.get(reverse("home"))
        content = response.content.decode()
        assert 'id="copyNameBtn"' in content
        assert 'id="copyTagsBtn"' in content


# ---------------------------------------------------------------------------
# Vocabulary manage view — GET
# ---------------------------------------------------------------------------
class TestVocabularyManageGet:
    """Tests for the ``vocabulary_manage`` view (GET ``/vocabulary/``)."""

    def test_returns_200(self, client: Client) -> None:
        response = client.get(reverse("vocabulary_manage"))
        assert response.status_code == 200

    def test_uses_correct_template(self, client: Client) -> None:
        response = client.get(reverse("vocabulary_manage"))
        assert "naming/vocabulary.html" in [t.name for t in response.templates]

    def test_context_has_vocab_and_field_list(self, client: Client) -> None:
        response = client.get(reverse("vocabulary_manage"))
        assert "vocab" in response.context
        assert "field_list" in response.context

    def test_field_list_contains_expected_tuples(self, client: Client) -> None:
        response = client.get(reverse("vocabulary_manage"))
        field_list = response.context["field_list"]
        field_names = [name for name, _label in field_list]
        assert "owner" in field_names
        assert "provider" in field_names
        assert "environment" in field_names
        assert "resource_type" in field_names
        assert "purpose" in field_names

    def test_vocab_dict_has_expected_keys(self, client: Client) -> None:
        response = client.get(reverse("vocabulary_manage"))
        vocab = response.context["vocab"]
        assert "owner" in vocab


# ---------------------------------------------------------------------------
# Vocabulary manage view — POST (adding flat entry)
# ---------------------------------------------------------------------------
class TestVocabularyManagePostFlat:
    """Tests for adding a flat vocabulary entry via POST."""

    def test_add_flat_owner_entry(self, client: Client, tmp_path: Path) -> None:
        dest = _patch_vocab(tmp_path)
        with patch("naming.views.get_vocab", lambda: get_vocab(dest)), \
             patch("naming.views.save_vocab", lambda data: save_vocab(data, dest)):
            response = client.post(
                reverse("vocabulary_manage"),
                {"field": "owner", "code": "tst", "label": "TestOwner"},
            )
        assert response.status_code == 302  # redirect
        reloaded = get_vocab(dest)
        assert reloaded["owner"]["tst"] == "TestOwner"

    def test_add_provider_entry(self, client: Client, tmp_path: Path) -> None:
        dest = _patch_vocab(tmp_path)
        with patch("naming.views.get_vocab", lambda: get_vocab(dest)), \
             patch("naming.views.save_vocab", lambda data: save_vocab(data, dest)):
            response = client.post(
                reverse("vocabulary_manage"),
                {"field": "provider", "code": "vlt", "label": "Vultr"},
            )
        assert response.status_code == 302
        reloaded = get_vocab(dest)
        assert reloaded["provider"]["vlt"] == "Vultr"

    def test_code_is_lowercased(self, client: Client, tmp_path: Path) -> None:
        dest = _patch_vocab(tmp_path)
        with patch("naming.views.get_vocab", lambda: get_vocab(dest)), \
             patch("naming.views.save_vocab", lambda data: save_vocab(data, dest)):
            client.post(
                reverse("vocabulary_manage"),
                {"field": "owner", "code": "TST", "label": "TestOwner"},
            )
        reloaded = get_vocab(dest)
        assert "tst" in reloaded["owner"]
        assert "TST" not in reloaded["owner"]

    def test_empty_code_does_not_save(self, client: Client, tmp_path: Path) -> None:
        dest = _patch_vocab(tmp_path)
        original = get_vocab(dest)
        with patch("naming.views.get_vocab", lambda: get_vocab(dest)), \
             patch("naming.views.save_vocab", lambda data: save_vocab(data, dest)):
            response = client.post(
                reverse("vocabulary_manage"),
                {"field": "owner", "code": "", "label": "NoCode"},
            )
        # Should render the page (200), not redirect (302)
        assert response.status_code == 200
        reloaded = get_vocab(dest)
        assert reloaded["owner"] == original["owner"]

    def test_empty_label_does_not_save(self, client: Client, tmp_path: Path) -> None:
        dest = _patch_vocab(tmp_path)
        original = get_vocab(dest)
        with patch("naming.views.get_vocab", lambda: get_vocab(dest)), \
             patch("naming.views.save_vocab", lambda data: save_vocab(data, dest)):
            response = client.post(
                reverse("vocabulary_manage"),
                {"field": "owner", "code": "xyz", "label": ""},
            )
        assert response.status_code == 200
        reloaded = get_vocab(dest)
        assert reloaded["owner"] == original["owner"]

    def test_cannot_write_to_tags_field(self, client: Client, tmp_path: Path) -> None:
        dest = _patch_vocab(tmp_path)
        original_tags = get_vocab(dest)["tags"]
        with patch("naming.views.get_vocab", lambda: get_vocab(dest)), \
             patch("naming.views.save_vocab", lambda data: save_vocab(data, dest)):
            client.post(
                reverse("vocabulary_manage"),
                {"field": "tags", "code": "hack", "label": "Hacked"},
            )
        reloaded = get_vocab(dest)
        assert "hack" not in reloaded.get("tags", {})


# ---------------------------------------------------------------------------
# Vocabulary manage view — POST (adding purpose with category)
# ---------------------------------------------------------------------------
class TestVocabularyManagePostPurpose:
    """Tests for adding a nested purpose entry via POST."""

    def test_add_purpose_to_existing_category(self, client: Client, tmp_path: Path) -> None:
        dest = _patch_vocab(tmp_path)
        with patch("naming.views.get_vocab", lambda: get_vocab(dest)), \
             patch("naming.views.save_vocab", lambda data: save_vocab(data, dest)):
            response = client.post(
                reverse("vocabulary_manage"),
                {"field": "purpose", "code": "proxy", "label": "Proxy", "category": "infrastructure"},
            )
        assert response.status_code == 302
        reloaded = get_vocab(dest)
        assert reloaded["purpose"]["infrastructure"]["proxy"] == "Proxy"

    def test_add_purpose_creates_new_category(self, client: Client, tmp_path: Path) -> None:
        dest = _patch_vocab(tmp_path)
        with patch("naming.views.get_vocab", lambda: get_vocab(dest)), \
             patch("naming.views.save_vocab", lambda data: save_vocab(data, dest)):
            response = client.post(
                reverse("vocabulary_manage"),
                {"field": "purpose", "code": "mc", "label": "Minecraft", "category": "gaming"},
            )
        assert response.status_code == 302
        reloaded = get_vocab(dest)
        assert "gaming" in reloaded["purpose"]
        assert reloaded["purpose"]["gaming"]["mc"] == "Minecraft"

    def test_purpose_without_category_does_not_save(self, client: Client, tmp_path: Path) -> None:
        """Purpose entries require a category — without it, nothing should be saved."""
        dest = _patch_vocab(tmp_path)
        original = get_vocab(dest)
        with patch("naming.views.get_vocab", lambda: get_vocab(dest)), \
             patch("naming.views.save_vocab", lambda data: save_vocab(data, dest)):
            response = client.post(
                reverse("vocabulary_manage"),
                {"field": "purpose", "code": "test", "label": "Test", "category": ""},
            )
        # Falls through to GET render (no redirect)
        assert response.status_code == 200
        reloaded = get_vocab(dest)
        assert reloaded["purpose"] == original["purpose"]
