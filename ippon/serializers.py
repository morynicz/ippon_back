from rest_framework import serializers

from ippon.models import Club, Player, Tournament


class ClubSerializer(serializers.ModelSerializer):
    class Meta:
        model = Club
        fields = ('id', 'name', 'webpage', 'description', 'city')


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ('id', 'name', 'surname', 'rank', 'sex', 'birthday', 'club_id')

class TournamentSerializer(serializers.ModelSerializer):
    class Meta:
        model= Tournament
        fields = (
            'id',
            'name',
            'date',
            'city',
            'address',
            'description',
            'webpage',
            'team_size',
            'group_match_length',
            'ko_match_length',
            'final_match_length',
            'finals_depth',
            'age_constraint',
            'sex_constraint',
            'rank_constraint',
            'rank_constraint_value',
            'age_constraint_value'
        )
