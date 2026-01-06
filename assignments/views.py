from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from assignments.services import assign_policy_to_device

class AssignPolicyView(APIView):
    def post(self, request, device_id, policy_id):
        assignment = assign_policy_to_device(device_id, policy_id)
        return Response(
            {
                "device_id": device_id,
                "policy_id": policy_id,
                "status": assignment.status,
            },
            status=status.HTTP_202_ACCEPTED,
        )
