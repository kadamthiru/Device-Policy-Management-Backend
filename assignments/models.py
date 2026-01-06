from django.db import models
from devices.models import Device
from policies.models import Policy, PolicyVersion

class DevicePolicyAssignment(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING"
        APPLIED = "APPLIED"
        FAILED = "FAILED"

    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name="policy_assignments"
    )
    policy = models.ForeignKey(
        Policy,
        on_delete=models.CASCADE
    )
    applied_version = models.ForeignKey(
        PolicyVersion,
        on_delete=models.PROTECT
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    created_at = models.DateTimeField(auto_now_add=True)
