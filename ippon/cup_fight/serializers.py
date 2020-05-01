from rest_framework import serializers

import ippon.models


class CupFightSerializer(serializers.ModelSerializer):
    class Meta:
        model = ippon.models.cup_fight.CupFight
        fields = (
            'id',
            'team_fight',
            'cup_phase',
            'previous_shiro_fight',
            'previous_aka_fight'
        )