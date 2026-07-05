from django import forms
from .models import Resource, ResourceGroup
from .vocab import get_choices, get_purpose_choices, get_purpose_flat


class ResourceGroupForm(forms.ModelForm):
    """Form for creating / editing a resource group."""

    class Meta:
        model = ResourceGroup
        fields = ["name", "description", "color"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-input", "placeholder": "e.g. Blog Stack",
            }),
            "description": forms.Textarea(attrs={
                "class": "form-input", "rows": 3, "placeholder": "What is this group for?",
            }),
            "color": forms.TextInput(attrs={
                "class": "form-input", "type": "color",
                "style": "height: 42px; padding: 4px;",
            }),
        }


class ResourceForm(forms.ModelForm):
    """
    Form for creating / editing a resource.

    Dropdowns are populated from vocabulary.yaml.
    Each field also supports a "custom" option — the JS handles showing
    a text input when "custom" is selected.
    """

    # Custom text fields (hidden by default, shown by JS when "custom" is picked)
    owner_custom = forms.CharField(max_length=10, required=False, widget=forms.TextInput(attrs={
        "class": "form-input custom-input", "placeholder": "e.g. ops", "id": "id_owner_custom",
    }))
    provider_custom = forms.CharField(max_length=10, required=False, widget=forms.TextInput(attrs={
        "class": "form-input custom-input", "placeholder": "e.g. vlt", "id": "id_provider_custom",
    }))
    environment_custom = forms.CharField(max_length=10, required=False, widget=forms.TextInput(attrs={
        "class": "form-input custom-input", "placeholder": "e.g. dmz", "id": "id_environment_custom",
    }))
    resource_type_custom = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={
        "class": "form-input custom-input", "placeholder": "e.g. nas", "id": "id_resource_type_custom",
    }))
    purpose_custom = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={
        "class": "form-input custom-input", "placeholder": "e.g. plex", "id": "id_purpose_custom",
    }))

    class Meta:
        model = Resource
        fields = ["groups", "owner", "provider", "environment", "resource_type", "purpose", "instance", "notes"]
        widgets = {
            "instance": forms.NumberInput(attrs={
                "class": "form-input", "min": 1, "max": 999, "value": 1,
            }),
            "notes": forms.Textarea(attrs={
                "class": "form-input", "rows": 3, "placeholder": "Optional notes…",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Resource Groups multiselect
        self.fields["groups"].widget = forms.SelectMultiple(
            choices=[(g.pk, g.name) for g in ResourceGroup.objects.all()],
            attrs={"class": "form-select", "id": "id_groups", "style": "height: 120px;"},
        )

        # Build dropdown choices dynamically from vocabulary.yaml
        custom_option = [("__custom__", "✏️ Custom…")]

        owner_choices = [("", "Select owner…")] + get_choices("owner") + custom_option
        provider_choices = [("", "Select provider…")] + get_choices("provider") + custom_option
        env_choices = [("", "Select environment…")] + get_choices("environment") + custom_option
        rt_choices = [("", "Select resource type…")] + get_choices("resource_type") + custom_option
        purpose_choices = [("", "Select purpose…")] + get_purpose_flat() + custom_option

        self.fields["owner"].widget = forms.Select(
            choices=owner_choices, attrs={"class": "form-select", "id": "id_owner"}
        )
        self.fields["provider"].widget = forms.Select(
            choices=provider_choices, attrs={"class": "form-select", "id": "id_provider"}
        )
        self.fields["environment"].widget = forms.Select(
            choices=env_choices, attrs={"class": "form-select", "id": "id_environment"}
        )
        self.fields["resource_type"].widget = forms.Select(
            choices=rt_choices, attrs={"class": "form-select", "id": "id_resource_type"}
        )
        self.fields["purpose"].widget = forms.Select(
            choices=purpose_choices, attrs={"class": "form-select", "id": "id_purpose"}
        )

    def clean(self):
        cleaned = super().clean()
        # For each identity field, if "__custom__" was selected, use the custom text input
        for field in ["owner", "provider", "environment", "resource_type", "purpose"]:
            if cleaned.get(field) == "__custom__":
                custom_val = cleaned.get(f"{field}_custom", "").strip().lower()
                if not custom_val:
                    self.add_error(field, "Please enter a custom value.")
                else:
                    cleaned[field] = custom_val
        return cleaned
