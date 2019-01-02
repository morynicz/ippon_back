from rest_framework import serializers

import ippon.tournament


class TournamentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ippon.tournament.tournament.Tournament
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