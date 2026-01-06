from django.db import transaction
from devices.models import Device
from policies.models import Policy, PolicyVersion
from assignments.models import DevicePolicyAssignment
from jobs.tasks import apply_policy_to_device

def assign_policy_to_device(device_id, policy_id):
    """
    Assigns the current version of a policy to a device.
    Idempotent and safe under concurrency.
    """

    with transaction.atomic():
        device = Device.objects.select_for_update().get(id=device_id)
        policy = Policy.objects.select_for_update().get(id=policy_id)

        current_version = PolicyVersion.objects.get(
            policy=policy,
            is_current=True
        )

        assignment, created = DevicePolicyAssignment.objects.get_or_create(
            device=device,
            policy=policy,
            defaults={
                "applied_version": current_version,
                "status": DevicePolicyAssignment.Status.PENDING,
            }
        )

        if not created:
            # Already assigned → update version if needed
            assignment.applied_version = current_version
            assignment.status = DevicePolicyAssignment.Status.PENDING
            assignment.save()

        apply_policy_to_device.delay(assignment.id)

        return assignment
