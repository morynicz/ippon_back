from rest_framework import serializers

import ippon.models


class GroupFightSerializer(serializers.ModelSerializer):
    class Meta:
        model = ippon.models.group_fight.GroupFight
        fields = (
            'id',
            'team_fight',
            'group'
        )