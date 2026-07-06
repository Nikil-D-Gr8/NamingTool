"""Tests for :mod:`naming.vocab` — the YAML vocabulary loader."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from naming.vocab import (
    ChoiceList,
    GroupedChoices,
    TagSuggestions,
    VocabDict,
    _load_raw,
    get_choices,
    get_purpose_choices,
    get_purpose_flat,
    get_tag_suggestions,
    get_vocab,
    save_vocab,
)


# ---------------------------------------------------------------------------
# _load_raw
# ---------------------------------------------------------------------------
class TestLoadRaw:
    """Tests for the internal ``_load_raw`` helper."""

    def test_returns_dict(self, vocab_path: Path) -> None:
        result = _load_raw(vocab_path)
        assert isinstance(result, dict)

    def test_contains_expected_top_level_keys(self, vocab_path: Path) -> None:
        result = _load_raw(vocab_path)
        for key in ("owner", "provider", "environment", "resource_type", "purpose", "tags"):
            assert key in result, f"Missing top-level key: {key}"

    def test_raises_on_missing_file(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            _load_raw(tmp_path / "nonexistent.yaml")


# ---------------------------------------------------------------------------
# get_vocab
# ---------------------------------------------------------------------------
class TestGetVocab:
    """Tests for :func:`get_vocab`."""

    def test_returns_full_dict(self, vocab_path: Path) -> None:
        vocab: VocabDict = get_vocab(vocab_path)
        assert "owner" in vocab
        assert "tags" in vocab

    def test_owner_values(self, vocab_path: Path) -> None:
        vocab = get_vocab(vocab_path)
        assert vocab["owner"]["nik"] == "Nikil"
        assert vocab["owner"]["lab"] == "Lab"


# ---------------------------------------------------------------------------
# get_choices  (flat fields)
# ---------------------------------------------------------------------------
class TestGetChoicesFlat:
    """Tests for :func:`get_choices` with flat (non-nested) fields."""

    def test_owner_choices(self, vocab_path: Path) -> None:
        choices: ChoiceList = get_choices("owner", vocab_path)
        assert ("nik", "Nikil") in choices
        assert ("lab", "Lab") in choices

    def test_provider_choices(self, vocab_path: Path) -> None:
        choices = get_choices("provider", vocab_path)
        assert ("hom", "Home Lab") in choices
        assert ("aws", "AWS") in choices

    def test_environment_choices(self, vocab_path: Path) -> None:
        choices = get_choices("environment", vocab_path)
        assert ("prd", "Production") in choices
        assert ("dev", "Development") in choices

    def test_resource_type_choices(self, vocab_path: Path) -> None:
        choices = get_choices("resource_type", vocab_path)
        assert ("vm", "Virtual Machine") in choices
        assert ("ct", "Container") in choices

    def test_returns_list_of_tuples(self, vocab_path: Path) -> None:
        choices = get_choices("owner", vocab_path)
        assert isinstance(choices, list)
        for item in choices:
            assert isinstance(item, tuple)
            assert len(item) == 2

    def test_unknown_field_returns_empty(self, vocab_path: Path) -> None:
        choices = get_choices("nonexistent_field", vocab_path)
        assert choices == []


# ---------------------------------------------------------------------------
# get_choices  (nested fields — e.g. purpose)
# ---------------------------------------------------------------------------
class TestGetChoicesNested:
    """Tests for :func:`get_choices` with the nested *purpose* field."""

    def test_purpose_flattened_with_category(self, vocab_path: Path) -> None:
        choices = get_choices("purpose", vocab_path)
        # Should have code + "label (category)" format
        assert ("core", "Core (infrastructure)") in choices
        assert ("blog", "Blog (applications)") in choices

    def test_purpose_length(self, vocab_path: Path) -> None:
        choices = get_choices("purpose", vocab_path)
        # fixture has 2 infra + 1 apps = 3
        assert len(choices) == 3


# ---------------------------------------------------------------------------
# get_purpose_choices  (grouped)
# ---------------------------------------------------------------------------
class TestGetPurposeChoices:
    """Tests for :func:`get_purpose_choices` (optgroup-style)."""

    def test_returns_grouped_list(self, vocab_path: Path) -> None:
        grouped: GroupedChoices = get_purpose_choices(vocab_path)
        assert isinstance(grouped, list)
        # Two categories in fixture: infrastructure, applications
        assert len(grouped) == 2

    def test_category_labels_are_title_case(self, vocab_path: Path) -> None:
        grouped = get_purpose_choices(vocab_path)
        labels = [label for label, _choices in grouped]
        assert "Infrastructure" in labels
        assert "Applications" in labels

    def test_items_inside_group(self, vocab_path: Path) -> None:
        grouped = get_purpose_choices(vocab_path)
        infra = next(items for label, items in grouped if label == "Infrastructure")
        assert ("core", "Core") in infra
        assert ("backup", "Backup") in infra


# ---------------------------------------------------------------------------
# get_purpose_flat
# ---------------------------------------------------------------------------
class TestGetPurposeFlat:
    """Tests for :func:`get_purpose_flat`."""

    def test_returns_flat_list(self, vocab_path: Path) -> None:
        choices: ChoiceList = get_purpose_flat(vocab_path)
        assert isinstance(choices, list)
        # 2 infra + 1 apps = 3
        assert len(choices) == 3

    def test_contains_expected_entries(self, vocab_path: Path) -> None:
        choices = get_purpose_flat(vocab_path)
        assert ("core", "Core") in choices
        assert ("blog", "Blog") in choices


# ---------------------------------------------------------------------------
# get_tag_suggestions
# ---------------------------------------------------------------------------
class TestGetTagSuggestions:
    """Tests for :func:`get_tag_suggestions`."""

    def test_returns_dict(self, vocab_path: Path) -> None:
        tags: TagSuggestions = get_tag_suggestions(vocab_path)
        assert isinstance(tags, dict)

    def test_has_expected_categories(self, vocab_path: Path) -> None:
        tags = get_tag_suggestions(vocab_path)
        assert "ownership" in tags
        assert "network" in tags

    def test_category_values_are_lists(self, vocab_path: Path) -> None:
        tags = get_tag_suggestions(vocab_path)
        assert isinstance(tags["ownership"], list)
        assert "owner" in tags["ownership"]
        assert "team" in tags["ownership"]


# ---------------------------------------------------------------------------
# save_vocab  (round-trip)
# ---------------------------------------------------------------------------
class TestSaveVocab:
    """Tests for :func:`save_vocab` — write + read-back round-trip."""

    def test_round_trip_preserves_data(self, vocab_path: Path) -> None:
        original = get_vocab(vocab_path)
        save_vocab(original, vocab_path)
        reloaded = get_vocab(vocab_path)
        assert reloaded == original

    def test_adding_new_entry_persists(self, vocab_path: Path) -> None:
        vocab = get_vocab(vocab_path)
        vocab["owner"]["tst"] = "TestOwner"
        save_vocab(vocab, vocab_path)

        reloaded = get_vocab(vocab_path)
        assert reloaded["owner"]["tst"] == "TestOwner"

    def test_adding_new_purpose_category(self, vocab_path: Path) -> None:
        vocab = get_vocab(vocab_path)
        vocab["purpose"]["gaming"] = {"mc": "Minecraft"}
        save_vocab(vocab, vocab_path)

        reloaded = get_vocab(vocab_path)
        assert reloaded["purpose"]["gaming"]["mc"] == "Minecraft"

    def test_written_file_is_valid_yaml(self, vocab_path: Path) -> None:
        vocab = get_vocab(vocab_path)
        vocab["owner"]["new"] = "NewOwner"
        save_vocab(vocab, vocab_path)

        with open(vocab_path) as fh:
            parsed = yaml.safe_load(fh)
        assert isinstance(parsed, dict)
        assert parsed["owner"]["new"] == "NewOwner"
