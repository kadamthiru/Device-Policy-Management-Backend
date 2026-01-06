from rest_framework import serializers
from devices.models import Device

class DeviceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ["id", "name", "platform"]
