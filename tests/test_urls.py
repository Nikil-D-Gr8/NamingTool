"""Tests for URL routing in the *naming* app and the project root."""

from __future__ import annotations

import pytest
from django.urls import NoReverseMatch, resolve, reverse


class TestURLResolves:
    """Verify that URL names resolve to the correct view functions."""

    def test_home_url_resolves(self) -> None:
        url = reverse("home")
        assert url == "/"
        match = resolve(url)
        assert match.func.__name__ == "home"

    def test_vocabulary_url_resolves(self) -> None:
        url = reverse("vocabulary_manage")
        assert url == "/vocabulary/"
        match = resolve(url)
        assert match.func.__name__ == "vocabulary_manage"


class TestURLReversal:
    """Verify that ``reverse()`` produces correct paths."""

    def test_home_reverse(self) -> None:
        assert reverse("home") == "/"

    def test_vocabulary_reverse(self) -> None:
        assert reverse("vocabulary_manage") == "/vocabulary/"

    def test_nonexistent_name_raises(self) -> None:
        with pytest.raises(NoReverseMatch):
            reverse("nonexistent_view")



