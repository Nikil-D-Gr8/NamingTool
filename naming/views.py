from django.shortcuts import render, redirect
from .vocab import get_vocab, get_choices, get_purpose_flat, get_tag_suggestions, save_vocab


def home(request):
    """Main page — name generator + tags copy-paster."""
    vocab = get_vocab()
    context = {
        "vocab": vocab,
        "owner_choices": get_choices("owner"),
        "provider_choices": get_choices("provider"),
        "environment_choices": get_choices("environment"),
        "resource_type_choices": get_choices("resource_type"),
        "purpose_choices": get_purpose_flat(),
        "tag_suggestions": get_tag_suggestions(),
    }
    return render(request, "naming/home.html", context)


def vocabulary_manage(request):
    """View and add new vocabulary entries."""
    vocab = get_vocab()

    if request.method == "POST":
        field = request.POST.get("field", "")
        code = request.POST.get("code", "").strip().lower()
        label = request.POST.get("label", "").strip()
        category = request.POST.get("category", "").strip().lower()

        if field and code and label:
            if field == "purpose" and category:
                if category not in vocab.get("purpose", {}):
                    vocab["purpose"][category] = {}
                vocab["purpose"][category][code] = label
            elif field in vocab and field != "purpose" and field != "tags":
                vocab[field][code] = label
            save_vocab(vocab)
            return redirect("vocabulary_manage")

    field_list = [
        ("owner", "Owners"),
        ("provider", "Providers"),
        ("environment", "Environments"),
        ("resource_type", "Resource Types"),
        ("purpose", "Purposes"),
    ]
    context = {"vocab": vocab, "field_list": field_list}
    return render(request, "naming/vocabulary.html", context)
