from django.contrib.auth.models import User
from rest_framework import serializers

import ippon.models as models
import ippon.event_models as event_models


class MinimalUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'username'
        )


class PointSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Point
        fields = (
            'id',
            'type',
            'player',
            'fight'
        )


class FightSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Fight
        fields = (
            'id',
            'aka',
            'shiro',
            'team_fight',
            'winner',
            'status'
        )


class TeamFightSerializer(serializers.ModelSerializer):
    aka_score = serializers.IntegerField(source='get_aka_wins', read_only=True)
    shiro_score = serializers.IntegerField(source='get_shiro_wins', read_only=True)

    class Meta:
        model = models.TeamFight
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


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Group
        fields = (
            'id',
            'name',
            'group_phase'
        )


class GroupPhaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.GroupPhase
        fields = (
            'id',
            'tournament',
            'fight_length',
            'name'
        )


class GroupFightSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.GroupFight
        fields = (
            'id',
            'team_fight',
            'group'
        )


class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'password'
        )
        extra_kwargs = {
            'password': {
                'write_only': True,
            },
        }


class CupPhaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CupPhase
        fields = (
            'id',
            'tournament',
            'name',
            'fight_length',
            'final_fight_length',
            'number_of_positions'
        )


class CupFightSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CupFight
        fields = (
            'id',
            'team_fight',
            'cup_phase',
            'previous_shiro_fight',
            'previous_aka_fight'
        )


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = event_models.Event
        fields = (
            'id',
            'name',
            'description',
            'icon',
            'banner',
            'start_time',
            'registration_start_time',
            'registration_end_time',
            'registration_is_open',
            'has_started'
        )
