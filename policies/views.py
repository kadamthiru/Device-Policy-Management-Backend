from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from policies.serializers import PolicyCreateSerializer
from policies.services import create_policy_version
from policies.services import rollback_policy_version


class PolicyCreateView(APIView):
    def post(self, request):
        serializer = PolicyCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PolicyVersionCreateView(APIView):
    def post(self, request, policy_id):
        payload = request.data.get("payload", {})
        version = create_policy_version(policy_id, payload)
        return Response(
            {
                "policy_id": policy_id,
                "version": version.version_number,
                "is_current": version.is_current,
            },
            status=status.HTTP_201_CREATED,
        )



class PolicyRollbackView(APIView):
    def post(self, request, policy_id, version_id):
        rollback_policy_version(policy_id, version_id)
        return Response(
            {"status": "rollback initiated"},
            status=status.HTTP_202_ACCEPTED
        )