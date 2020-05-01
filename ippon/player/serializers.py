from rest_framework import serializers

import ippon.models.player as pm


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = pm.Player
        fields = ('id', 'name', 'surname', 'rank', 'sex', 'birthday', 'club_id')


class ShallowPlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = pm.Player
        fields = ('id', 'name', 'surname')
