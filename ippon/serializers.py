from rest_framework import serializers

from ippon.models import Club, Player


class ClubSerializer(serializers.ModelSerializer):
    class Meta:
        model = Club
        fields = ('id', 'name', 'webpage', 'description', 'city')


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ('id', 'name', 'surname', 'rank', 'sex', 'birthday', 'club_id')
