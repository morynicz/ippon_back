from rest_framework import serializers

import ippon.team_fight.models as tfm


class TeamFightSerializer(serializers.ModelSerializer):
    aka_score = serializers.IntegerField(source='get_aka_wins', read_only=True)
    shiro_score = serializers.IntegerField(source='get_shiro_wins', read_only=True)

    class Meta:
        model = tfm.TeamFight
        fields = (
            'id',
            'aka_team',
            'shiro_team',
            'tournament',
            'winner',
            'status',
            'aka_score',
            'shiro_score'
        )
