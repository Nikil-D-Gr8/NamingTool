from django.contrib import admin
from .models import Resource, ResourceGroup


@admin.register(ResourceGroup)
class ResourceGroupAdmin(admin.ModelAdmin):
    list_display = ["name", "resource_count", "color", "created_at"]
    search_fields = ["name"]


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ["rid", "name", "get_groups", "owner", "provider", "environment", "resource_type", "purpose", "instance", "created_at"]
    list_filter = ["groups", "owner", "provider", "environment", "resource_type"]
    search_fields = ["owner", "provider", "purpose", "groups__name"]
    readonly_fields = ["rid", "name", "created_at", "updated_at"]

    def get_groups(self, obj):
        return ", ".join([g.name for g in obj.groups.all()])
    get_groups.short_description = 'Groups'
