from rest_framework import serializers
from policies.models import Policy

class PolicyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Policy
        fields = ["id", "name", "type"]
