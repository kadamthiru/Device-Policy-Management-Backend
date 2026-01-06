import uuid
from django.db import models
from django.db.models import Q

class Policy(models.Model):
    class PolicyType(models.TextChoices):
        PASSCODE = "PASSCODE"
        WIFI = "WIFI"
        RESTRICTIONS = "RESTRICTIONS"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    type = models.CharField(
        max_length=30,
        choices=PolicyType.choices
    )
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.type})"


class PolicyVersion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    policy = models.ForeignKey(
        Policy,
        on_delete=models.CASCADE,
        related_name="versions"
    )

    version_number = models.PositiveIntegerField()
    payload = models.JSONField()
    is_current = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["policy", "version_number"],
                name="unique_policy_version"
            ),
            models.UniqueConstraint(
                fields=["policy"],
                condition=Q(is_current=True),
                name="only_one_current_version"
            )
        ]
        ordering = ["-version_number"]
