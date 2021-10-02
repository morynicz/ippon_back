from rest_framework import serializers

import ippon.models.fight


class FightSerializer(serializers.ModelSerializer):
    class Meta:
        model = ippon.models.fight.Fight
        fields = ("id", "aka", "shiro", "team_fight", "winner", "status")
