from rest_framework import serializers

import ippon.models


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ippon.models.group.Group
        fields = ("id", "name", "group_phase")
