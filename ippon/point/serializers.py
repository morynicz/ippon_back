from rest_framework import serializers

import ippon.point


class PointSerializer(serializers.ModelSerializer):
    class Meta:
        model = ippon.point.models.Point
        fields = (
            'id',
            'type',
            'player',
            'fight'
        )