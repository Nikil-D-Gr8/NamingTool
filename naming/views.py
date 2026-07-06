"""
Views for the NamingTool — a stateless name generator and tag builder.

Only two views:

* **home** — renders the name-generator + tag-builder page.
* **vocabulary_manage** — lets users browse and extend the YAML vocabulary.
"""

from __future__ import annotations

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render

from .vocab import (
    get_choices,
    get_purpose_flat,
    get_tag_suggestions,
    get_vocab,
    save_vocab,
)


def home(request: HttpRequest) -> HttpResponse:
    """Main page — name generator + tags copy-paster."""
    vocab = get_vocab()
    context: dict[str, object] = {
        "vocab": vocab,
        "owner_choices": get_choices("owner"),
        "provider_choices": get_choices("provider"),
        "environment_choices": get_choices("environment"),
        "resource_type_choices": get_choices("resource_type"),
        "purpose_choices": get_purpose_flat(),
        "tag_suggestions": get_tag_suggestions(),
    }
    return render(request, "naming/home.html", context)


def vocabulary_manage(request: HttpRequest) -> HttpResponse | HttpResponseRedirect:
    """View and add new vocabulary entries via POST, or browse them via GET."""
    vocab = get_vocab()

    if request.method == "POST":
        field: str = request.POST.get("field", "")
        code: str = request.POST.get("code", "").strip().lower()
        label: str = request.POST.get("label", "").strip()
        category: str = request.POST.get("category", "").strip().lower()

        changed: bool = False
        if field and code and label:
            if field == "purpose" and category:
                if category not in vocab.get("purpose", {}):
                    vocab["purpose"][category] = {}
                vocab["purpose"][category][code] = label
                changed = True
            elif field in vocab and field not in ("purpose", "tags"):
                vocab[field][code] = label
                changed = True

            if changed:
                save_vocab(vocab)
                return redirect("vocabulary_manage")

    field_list: list[tuple[str, str]] = [
        ("owner", "Owners"),
        ("provider", "Providers"),
        ("environment", "Environments"),
        ("resource_type", "Resource Types"),
        ("purpose", "Purposes"),
    ]
    context: dict[str, object] = {"vocab": vocab, "field_list": field_list}
    return render(request, "naming/vocabulary.html", context)
