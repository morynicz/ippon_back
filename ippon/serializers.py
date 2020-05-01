from django.contrib.auth.models import User
from rest_framework import serializers

import ippon.models as models
import ippon.event_models as event_models
import ippon.models.group_phase


class MinimalUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'username'
        )


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ippon.models.group.Group
        fields = (
            'id',
            'name',
            'group_phase'
        )


class GroupFightSerializer(serializers.ModelSerializer):
    class Meta:
        model = ippon.models.group_fight.GroupFight
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
