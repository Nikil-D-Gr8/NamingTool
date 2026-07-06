"""Shared pytest fixtures for the NamingTool test suite."""

from __future__ import annotations

from pathlib import Path

import pytest

#: Path to the small vocabulary fixture shipped with tests.
FIXTURE_DIR: Path = Path(__file__).resolve().parent / "fixtures"
TEST_VOCAB_PATH: Path = FIXTURE_DIR / "test_vocabulary.yaml"


@pytest.fixture()
def vocab_path(tmp_path: Path) -> Path:
    """Return a *writable* copy of the test vocabulary YAML.

    Each test gets its own copy so writes don't bleed between tests.
    """
    dest = tmp_path / "vocabulary.yaml"
    dest.write_text(TEST_VOCAB_PATH.read_text())
    return dest
