from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Count, Q
from django.contrib.auth.decorators import login_required
from .models import Resource, ResourceGroup
from .forms import ResourceForm, ResourceGroupForm
from .vocab import get_vocab, get_choices, get_purpose_flat, get_tag_suggestions, save_vocab
import json


@login_required
def dashboard(request):
    """Main dashboard with stats and recent resources."""
    resources = Resource.objects.all()
    total = resources.count()
    groups = ResourceGroup.objects.annotate(count=Count("resources"))

    # Stats by resource type (top 8)
    by_type = (
        resources.values("resource_type")
        .annotate(count=Count("resource_type"))
        .order_by("-count")[:8]
    )

    # Stats by environment
    by_env = (
        resources.values("environment")
        .annotate(count=Count("environment"))
        .order_by("-count")
    )

    # Recent resources
    recent = resources.select_related("group")[:10]

    context = {
        "total": total,
        "by_type": list(by_type),
        "by_env": list(by_env),
        "recent": recent,
        "groups": groups,
        "group_count": groups.count(),
    }
    return render(request, "naming/dashboard.html", context)


@login_required
def resource_list(request):
    """Filterable list of all resources."""
    resources = Resource.objects.select_related("group").all()

    # Simple search
    q = request.GET.get("q", "").strip()
    if q:
        resources = resources.filter(
            Q(owner__icontains=q)
            | Q(provider__icontains=q)
            | Q(resource_type__icontains=q)
            | Q(purpose__icontains=q)
            | Q(environment__icontains=q)
            | Q(notes__icontains=q)
            | Q(group__name__icontains=q)
        )

    # Filters
    for field in ["owner", "provider", "environment", "resource_type"]:
        val = request.GET.get(field, "").strip()
        if val:
            resources = resources.filter(**{field: val})

    # Group filter
    group_id = request.GET.get("group", "").strip()
    if group_id:
        resources = resources.filter(group_id=group_id)

    context = {
        "resources": resources,
        "q": q,
        "vocab": get_vocab(),
        "groups": ResourceGroup.objects.all(),
    }
    return render(request, "naming/resource_list.html", context)


@login_required
def resource_create(request):
    """Create a new resource."""
    if request.method == "POST":
        form = ResourceForm(request.POST)
        if form.is_valid():
            resource = form.save(commit=False)
            # Parse tags from the hidden JSON field
            tags_json = request.POST.get("tags_json", "{}")
            try:
                resource.tags = json.loads(tags_json)
            except json.JSONDecodeError:
                resource.tags = {}
            resource.save()
            return redirect("resource_detail", pk=resource.pk)
    else:
        form = ResourceForm()

    context = {
        "form": form,
        "tag_suggestions": get_tag_suggestions(),
    }
    return render(request, "naming/resource_create.html", context)


@login_required
def resource_detail(request, pk):
    """View a single resource's details."""
    resource = get_object_or_404(Resource.objects.select_related("group"), pk=pk)
    # Get sibling resources in the same group
    siblings = resource.group.resources.exclude(pk=resource.pk)[:10]
    return render(request, "naming/resource_detail.html", {
        "resource": resource,
        "siblings": siblings,
    })


@login_required
def resource_edit(request, pk):
    """Edit an existing resource."""
    resource = get_object_or_404(Resource, pk=pk)
    if request.method == "POST":
        form = ResourceForm(request.POST, instance=resource)
        if form.is_valid():
            resource = form.save(commit=False)
            tags_json = request.POST.get("tags_json", "{}")
            try:
                resource.tags = json.loads(tags_json)
            except json.JSONDecodeError:
                pass
            resource.save()
            return redirect("resource_detail", pk=resource.pk)
    else:
        form = ResourceForm(instance=resource)

    context = {
        "form": form,
        "resource": resource,
        "tag_suggestions": get_tag_suggestions(),
        "existing_tags_json": json.dumps(resource.tags),
    }
    return render(request, "naming/resource_edit.html", context)


@login_required
def resource_delete(request, pk):
    """Delete a resource."""
    resource = get_object_or_404(Resource, pk=pk)
    if request.method == "POST":
        resource.delete()
        return redirect("resource_list")
    return render(request, "naming/resource_delete.html", {"resource": resource})


@login_required
def api_next_instance(request):
    """
    AJAX endpoint: given identity fields, return the next available instance number.
    """
    owner = request.GET.get("owner", "")
    provider = request.GET.get("provider", "")
    env = request.GET.get("environment", "")
    rt = request.GET.get("resource_type", "")
    purpose = request.GET.get("purpose", "")

    existing = Resource.objects.filter(
        owner=owner, provider=provider, environment=env,
        resource_type=rt, purpose=purpose,
    ).values_list("instance", flat=True)

    next_inst = 1
    if existing:
        next_inst = max(existing) + 1

    return JsonResponse({"next_instance": next_inst})


@login_required
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


# ---- Resource Group views ----

@login_required
def group_list(request):
    """List all resource groups with their resource counts."""
    groups = ResourceGroup.objects.annotate(count=Count("resources")).order_by("name")
    return render(request, "naming/group_list.html", {"groups": groups})


@login_required
def group_create(request):
    """Create a new resource group."""
    if request.method == "POST":
        form = ResourceGroupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("group_list")
    else:
        form = ResourceGroupForm()
    return render(request, "naming/group_form.html", {"form": form, "title": "Create Resource Group"})


@login_required
def group_detail(request, pk):
    """View a resource group and all its resources."""
    group = get_object_or_404(ResourceGroup, pk=pk)
    resources = group.resources.all()
    return render(request, "naming/group_detail.html", {"group": group, "resources": resources})


@login_required
def group_edit(request, pk):
    """Edit a resource group."""
    group = get_object_or_404(ResourceGroup, pk=pk)
    if request.method == "POST":
        form = ResourceGroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            return redirect("group_detail", pk=group.pk)
    else:
        form = ResourceGroupForm(instance=group)
    return render(request, "naming/group_form.html", {"form": form, "group": group, "title": "Edit Group"})


@login_required
def group_delete(request, pk):
    """Delete a resource group (only if empty)."""
    group = get_object_or_404(ResourceGroup, pk=pk)
    if request.method == "POST":
        if group.resources.exists():
            from django.contrib import messages
            messages.error(request, f"Cannot delete '{group.name}' — it still has {group.resource_count} resource(s). Move or delete them first.")
            return redirect("group_detail", pk=group.pk)
        group.delete()
        return redirect("group_list")
    return render(request, "naming/group_delete.html", {"group": group})
