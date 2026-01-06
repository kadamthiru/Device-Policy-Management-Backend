from celery import shared_task
from django.db import transaction
from django.utils import timezone
from assignments.models import DevicePolicyAssignment
from jobs.models import PolicyExecutionJob

@shared_task(bind=True, max_retries=3)
def apply_policy_to_device(self, assignment_id):
    job = PolicyExecutionJob.objects.create(
        assignment_id=assignment_id,
        status=PolicyExecutionJob.Status.QUEUED
    )

    try:
        with transaction.atomic():
            assignment = (
                DevicePolicyAssignment.objects
                .select_for_update()
                .get(id=assignment_id)
            )

            job.status = PolicyExecutionJob.Status.RUNNING
            job.started_at = timezone.now()
            job.save()

            # Simulate policy application
            import time
            time.sleep(2)

            assignment.status = DevicePolicyAssignment.Status.APPLIED
            assignment.save()

            job.status = PolicyExecutionJob.Status.SUCCESS

    except Exception as exc:
        assignment.status = DevicePolicyAssignment.Status.FAILED
        assignment.save()

        job.status = PolicyExecutionJob.Status.FAILED
        job.error_message = str(exc)

        raise self.retry(exc=exc, countdown=5)

    finally:
        job.finished_at = timezone.now()
        job.save()
    