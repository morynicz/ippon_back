from django.contrib.auth.models import User
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from ippon.models import TournamentParticipation, TournamentAdmin, Team, GroupPhase, CupPhase, Tournament
import ippon.player.models as plm
import ippon.player.serializers as pls
import ippon.permissions as perms
from ippon.serializers import TournamentParticipationSerializer, TournamentAdminSerializer, MinimalUserSerializer, \
    TeamSerializer, GroupPhaseSerializer, CupPhaseSerializer, \
    TournamentSerializer


class TournamentViewSet(viewsets.ModelViewSet):
    queryset = Tournament.objects.all()
    serializer_class = TournamentSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          perms.IsTournamentAdminOrReadOnlyTournament)

    @action(methods=['get'], detail=True, permission_classes=(
            permissions.IsAuthenticated,
            perms.IsTournamentOwner))
    def participations(self, request, pk=None):
        get_object_or_404(self.queryset, pk=pk)
        serializer = TournamentParticipationSerializer(TournamentParticipation.objects.filter(tournament=pk), many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True, permission_classes=(
            permissions.IsAuthenticated,
            perms.IsTournamentOwner))
    def non_participants(self, request, pk=None):
        get_object_or_404(self.queryset, pk=pk)
        serializer = pls.PlayerSerializer(plm.Player.objects.exclude(participations__tournament=pk), many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True, permission_classes=(
            permissions.IsAuthenticated,
            perms.IsTournamentOwner))
    def participants(self, request, pk=None):
        get_object_or_404(self.queryset, pk=pk)
        serializer = pls.PlayerSerializer(
            plm.Player.objects.filter(participations__tournament=pk, participations__is_qualified=True), many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        tournament = serializer.save()
        ta = TournamentAdmin(user=self.request.user, tournament=tournament, is_master=True)
        ta.save()

    @action(methods=['get'], detail=True, permission_classes=(
            permissions.IsAuthenticated,
            perms.IsTournamentOwner))
    def admins(self, request, pk=None):
        get_object_or_404(self.queryset, pk=pk)
        serializer = TournamentAdminSerializer(TournamentAdmin.objects.filter(tournament=pk), many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True, permission_classes=(
            permissions.IsAuthenticated,
            perms.IsTournamentOwner))
    def non_admins(self, request, pk=None):
        get_object_or_404(self.queryset, pk=pk)
        serializer = MinimalUserSerializer(User.objects.exclude(tournaments__tournament=pk), many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True)
    def teams(self, request, pk=None):
        get_object_or_404(self.queryset, pk=pk)
        serializer = TeamSerializer(
            Team.objects.filter(tournament=pk), many=True)
        return Response(serializer.data)

    @action(
        methods=['get'],
        detail=True,
        url_name='group_phases')
    def group_phases(self, request, pk=None):
        get_object_or_404(self.queryset, pk=pk)
        serializer = GroupPhaseSerializer(GroupPhase.objects.filter(tournament=pk), many=True)
        return Response(serializer.data)

    @action(
        methods=['get'],
        detail=True,
        url_name='cup_phases')
    def cup_phases(self, request, pk=None):
        get_object_or_404(self.queryset, pk=pk)
        serializer = CupPhaseSerializer(CupPhase.objects.filter(tournament=pk), many=True)
        return Response(serializer.data)

    @action(
        methods=['get'],
        detail=True,
        url_name='not_assigned',
        permission_classes=[
            permissions.IsAuthenticated,
            perms.IsTournamentAdmin
        ]
    )
    def not_assigned(self, request, pk=None):
        players = plm.Player.objects.filter(participations__tournament=pk, participations__is_qualified=True).exclude(
            team_member__team__tournament=pk)
        serializer = pls.ShallowPlayerSerializer(players, many=True)
        return Response(serializer.data)
