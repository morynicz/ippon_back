from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

import ippon.models.club as cl


class ClubSerializer(serializers.ModelSerializer):
    class Meta:
        model = cl.Club
        fields = ('id', 'name', 'webpage', 'description', 'city')


class ClubAdminSerializer(serializers.ModelSerializer):
    club_id = serializers.IntegerField(source='club.id')
    user = serializers.DictField(source='get_user')

    class Meta:
        model = cl.ClubAdmin
        fields = (
            'id',
            'club_id',
            'user'
        )
        read_only_fields = ('user',)

    def create(self, validated_data):
        if not isinstance(self.initial_data['user']['id'], int):
            raise ValidationError('user id must be an integer')
        admin = cl.ClubAdmin.objects.create(
            user=User.objects.get(pk=self.initial_data['user']['id']),
            club=cl.Club.objects.get(pk=validated_data['club']['id']),
        )
        return admin
