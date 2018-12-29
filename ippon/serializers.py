from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from ippon.models import Club, Player, Tournament, TournamentParticipation, TournamentAdmin, Team, ClubAdmin, Point, \
    Fight, TeamFight, Group, GroupPhase, GroupFight


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
        model = Tournament
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


class TournamentParticipationSerializer(serializers.ModelSerializer):
    is_age_ok = serializers.BooleanField(source='check_is_age_ok', read_only=True)
    is_rank_ok = serializers.BooleanField(source='check_is_rank_ok', read_only=True)
    is_sex_ok = serializers.BooleanField(source='check_is_sex_ok', read_only=True)
    tournament_id = serializers.IntegerField(source='tournament.id')
    player = PlayerSerializer()

    class Meta:
        model = TournamentParticipation
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
        participation = TournamentParticipation.objects.create(
            player=Player.objects.get(pk=self.initial_data['player']['id']),
            tournament=Tournament.objects.get(pk=validated_data['tournament']['id'])
        )
        return participation

    def update(self, instance, validated_data):
        instance.is_paid = validated_data['is_paid']
        instance.is_registered = validated_data['is_registered']
        instance.is_qualified = validated_data['is_qualified']
        instance.notes = validated_data['notes']
        instance.save()
        return instance


class MinimalUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'username'
        )


class TournamentAdminSerializer(serializers.ModelSerializer):
    tournament_id = serializers.IntegerField(source='tournament.id')
    user = serializers.DictField(source='get_user')

    class Meta:
        model = TournamentAdmin
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
        admin = TournamentAdmin.objects.create(
            user=User.objects.get(pk=self.initial_data['user']['id']),
            tournament=Tournament.objects.get(pk=validated_data['tournament']['id']),
            is_master=False
        )
        return admin

    def update(self, instance, validated_data):
        instance.is_master = validated_data['is_master']
        instance.save()
        return instance


class ClubAdminSerializer(serializers.ModelSerializer):
    club_id = serializers.IntegerField(source='club.id')
    user = serializers.DictField(source='get_user')

    class Meta:
        model = ClubAdmin
        fields = (
            'id',
            'club_id',
            'user'
        )
        read_only_fields = ('user',)

    def create(self, validated_data):
        if not isinstance(self.initial_data['user']['id'], int):
            raise ValidationError('user id must be an integer')
        admin = ClubAdmin.objects.create(
            user=User.objects.get(pk=self.initial_data['user']['id']),
            club=Club.objects.get(pk=validated_data['club']['id']),
        )
        return admin


class TeamSerializer(serializers.ModelSerializer):
    members = serializers.ListField(read_only=True, source='get_member_ids',
                                    child=serializers.IntegerField(min_value=1))

    class Meta:
        model = Team
        fields = (
            'id',
            'name',
            'tournament',
            'members'
        )


class PointSerializer(serializers.ModelSerializer):
    class Meta:
        model = Point
        fields = (
            'id',
            'type',
            'player',
            'fight'
        )


class FightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fight
        fields = (
            'id',
            'aka',
            'shiro',
            'team_fight'
        )


class TeamFightSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamFight
        fields = (
            'id',
            'aka_team',
            'shiro_team',
            'tournament'
        )


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = (
            'id',
            'name',
            'group_phase'
        )


class GroupPhaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupPhase
        fields = (
            'id',
            'tournament',
            'fight_length',
            'name'
        )


class GroupFightSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupFight
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
