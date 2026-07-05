from django.db import models
from django.conf import settings


class ResourceGroup(models.Model):
    """
    A logical grouping of related resources.

    Examples: "Blog Stack", "Minecraft Server", "Core Network", etc.
    Every resource must belong to exactly one group.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="resource_groups")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, default="")
    color = models.CharField(
        max_length=7,
        default="#3b82f6",
        help_text="Hex color for the group badge (e.g. #3b82f6)",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        unique_together = [["user", "name"]]

    def __str__(self):
        return self.name

    @property
    def resource_count(self):
        return self.resources.count()


class Resource(models.Model):
    """
    A tracked resource with a canonical name and metadata.

    The name is computed from the identity fields:
        <owner>-<provider>-<environment>-<resource_type>-<purpose>-<instance>

    An internal sequential ID (R000001) is assigned automatically and never
    changes, even if the resource is renamed.
    """

    # Internal tracking ID — auto-incremented, never changes
    internal_id = models.AutoField(primary_key=True)

    # --- User Ownership ---
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="resources")

    # --- Resource Groups ---
    groups = models.ManyToManyField(
        ResourceGroup,
        related_name="resources",
        help_text="The resource groups this resource belongs to (at least one).",
    )

    # --- Identity fields (these compose the canonical name) ---
    owner = models.CharField(max_length=10)
    provider = models.CharField(max_length=10)
    environment = models.CharField(max_length=10)
    resource_type = models.CharField(max_length=20)
    purpose = models.CharField(max_length=50)
    instance = models.PositiveIntegerField(default=1)

    # --- Metadata ---
    tags = models.JSONField(default=dict, blank=True)
    notes = models.TextField(blank=True, default="")

    # --- Timestamps ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "owner", "provider", "environment", "resource_type", "purpose", "instance"],
                name="unique_resource_identity",
            )
        ]
        ordering = ["-created_at"]

    @property
    def rid(self):
        """Human-readable internal ID like R000001."""
        return f"R{self.internal_id:06d}"

    @property
    def name(self):
        """Canonical resource name."""
        return (
            f"{self.owner}-{self.provider}-{self.environment}"
            f"-{self.resource_type}-{self.purpose}-{self.instance:03d}"
        )

    def __str__(self):
        return f"[{self.rid}] {self.name}"
