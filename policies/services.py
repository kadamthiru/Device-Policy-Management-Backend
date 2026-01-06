from django.db import transaction
from django.db.models import Max
from policies.models import Policy, PolicyVersion
from assignments.models import DevicePolicyAssignment
# from jobs.tasks import apply_policy_to_device  # we will create this

def create_policy_version(policy_id, payload):
    """
    Creates a new immutable version for a policy.
    Ensures:
    - Sequential versioning
    - Only one current version
    - Safe under concurrency
    """

    with transaction.atomic():
        policy = Policy.objects.select_for_update().get(id=policy_id)

        latest_version = (
            PolicyVersion.objects
            .filter(policy=policy)
            .aggregate(max_version=Max("version_number"))
            .get("max_version") or 0
        )

        # Mark existing current version as non-current
        PolicyVersion.objects.filter(
            policy=policy,
            is_current=True
        ).update(is_current=False)

        new_version = PolicyVersion.objects.create(
            policy=policy,
            version_number=latest_version + 1,
            payload=payload,
            is_current=True
        )

        return new_version


def rollback_policy_version(policy_id, target_version_id):
    """
    Roll back a policy to a previous version.
    Ensures:
    - Only one current version
    - Safe under concurrency
    - Triggers re-application to devices
    """

    with transaction.atomic():
        policy = Policy.objects.select_for_update().get(id=policy_id)

        target_version = PolicyVersion.objects.select_for_update().get(
            id=target_version_id,
            policy=policy
        )

        # Mark current version as non-current
        PolicyVersion.objects.filter(
            policy=policy,
            is_current=True
        ).update(is_current=False)

        # Activate target version
        target_version.is_current = True
        target_version.save()

        # Re-apply policy to all assigned devices
        assignments = DevicePolicyAssignment.objects.filter(
            policy=policy
        )

        for assignment in assignments:
            assignment.applied_version = target_version
            assignment.status = DevicePolicyAssignment.Status.PENDING
            assignment.save()

            apply_policy_to_device.delay(assignment.id)
