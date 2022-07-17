from rest_framework import serializers

import ippon.models.team as tem


class TeamSerializer(serializers.ModelSerializer):
    members = serializers.ListField(
        read_only=True,
        source="get_member_ids",
        child=serializers.IntegerField(min_value=1),
    )

    class Meta:
        model = tem.Team
        fields = ("id", "name", "tournament", "members")
