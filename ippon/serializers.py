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
