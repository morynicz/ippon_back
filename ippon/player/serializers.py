from rest_framework import serializers

import ippon.player


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ippon.player.models.Player
        fields = ('id', 'name', 'surname', 'rank', 'sex', 'birthday', 'club_id')


class ShallowPlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ippon.player.models.Player
        fields = ('id', 'name', 'surname')