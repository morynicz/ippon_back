from rest_framework import serializers

from ippon.models import event as event_models


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