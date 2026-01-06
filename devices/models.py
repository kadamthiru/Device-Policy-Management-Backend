from django.db import models
import uuid

class Device(models.Model):
    class Platform(models.TextChoices):
        MACOS = "MACOS"
        IOS = "IOS"

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE"
        INACTIVE = "INACTIVE"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    platform = models.CharField(
        max_length=20,
        choices=Platform.choices
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.platform})"
