from rest_framework import serializers

import ippon.models


class GroupPhaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ippon.models.group_phase.GroupPhase
        fields = (
            'id',
            'tournament',
            'fight_length',
            'name'
        )
