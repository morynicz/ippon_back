from rest_framework import serializers

import ippon.models.event as em


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = em.Event
        fields = (
            "id",
            "name",
            "description",
            "icon",
            "banner",
            "start_time",
            "end_time",
            "registration_start_time",
            "registration_end_time",
            "registration_is_open",
            "has_started",
        )
