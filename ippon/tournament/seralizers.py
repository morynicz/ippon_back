from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

import ippon.models
import ippon.tournament.models as tm
import ippon.player.serializers as pls
import ippon.player.models as plm


class TournamentParticipationSerializer(serializers.ModelSerializer):
    is_age_ok = serializers.BooleanField(source='check_is_age_ok', read_only=True)
    is_rank_ok = serializers.BooleanField(source='check_is_rank_ok', read_only=True)
    is_sex_ok = serializers.BooleanField(source='check_is_sex_ok', read_only=True)
    tournament_id = serializers.IntegerField(source='tournament.id')
    player = pls.ShallowPlayerSerializer()

    class Meta:
        model = tm.TournamentParticipation
        fields = (
            'id',
            'is_paid',
            'is_registered',
            'is_qualified',
            'is_age_ok',
            'is_rank_ok',
            'is_sex_ok',
            'player',
            'tournament_id',
            'notes'
        )

    def create(self, validated_data):
        if not isinstance(self.initial_data['player']['id'], int):
            raise ValidationError('player.id must be an integer')
        filtered = plm.Player.objects.filter(pk=self.initial_data['player']['id'])
        if not filtered.exists():
            raise ValidationError('no such player')
        participation = tm.TournamentParticipation.objects.create(
            player=filtered.first(),
            tournament=tm.Tournament.objects.get(pk=validated_data['tournament']['id'])
        )
        return participation

    def update(self, instance, validated_data):
        instance.is_paid = validated_data['is_paid']
        instance.is_registered = validated_data['is_registered']
        instance.is_qualified = validated_data['is_qualified']
        instance.notes = validated_data['notes']
        instance.save()
        return instance


class TournamentAdminSerializer(serializers.ModelSerializer):
    tournament_id = serializers.IntegerField(source='tournament.id')
    user = serializers.DictField(source='get_user')

    class Meta:
        model = tm.TournamentAdmin
        fields = (
            'tournament_id',
            'id',
            'is_master',
            'user'
        )
        read_only_fields = ('user',)

    def create(self, validated_data):
        if not isinstance(self.initial_data['user']['id'], int):
            raise ValidationError('user.id must be an integer')
        admin = tm.TournamentAdmin.objects.create(
            user=User.objects.get(pk=self.initial_data['user']['id']),
            tournament=tm.Tournament.objects.get(pk=validated_data['tournament']['id']),
            is_master=False
        )
        return admin

    def update(self, instance, validated_data):
        instance.is_master = validated_data['is_master']
        instance.save()
        return instance


class TournamentSerializer(serializers.ModelSerializer):
    class Meta:
        model = tm.Tournament
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
