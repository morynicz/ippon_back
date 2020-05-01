from django.contrib.auth.models import User
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

import ippon.models.group_phase as gpm
import ippon.models.cup_phase as cpm
import ippon.models.team as tem
import ippon.player.serializers as pls
import ippon.models.player as plm
from ippon.user.serailzers import MinimalUserSerializer
from ippon.group_phase.serializers import GroupPhaseSerializer
import ippon.cup_phase.serializers as cps
import ippon.team.serializers as tes
import ippon.models.tournament as tm
import ippon.tournament.seralizers as ts
import ippon.tournament.permissions as tp


class TournamentParticipationViewSet(viewsets.ModelViewSet):
    queryset = tm.TournamentParticipation.objects.all()
    serializer_class = ts.TournamentParticipationSerializer
    permission_classes = (permissions.IsAuthenticated,
                          tp.IsTournamentAdminParticipantCreation)


class TournamentAdminViewSet(viewsets.ModelViewSet):
    queryset = tm.TournamentAdmin.objects.all()
    serializer_class = ts.TournamentAdminSerializer
    permission_classes = (permissions.IsAuthenticated,
                          tp.IsTournamentOwnerAdminCreation)


class TournamentViewSet(viewsets.ModelViewSet):
    queryset = tm.Tournament.objects.all()
    serializer_class = ts.TournamentSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          tp.IsTournamentAdminOrReadOnlyTournament)

    @action(methods=['get'], detail=True, permission_classes=(
            permissions.IsAuthenticated,
            tp.IsTournamentOwner))
    def participations(self, request, pk=None):
        get_object_or_404(self.queryset, pk=pk)
        serializer = ts.TournamentParticipationSerializer(tm.TournamentParticipation.objects.filter(tournament=pk),
                                                          many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True, permission_classes=(
            permissions.IsAuthenticated,
            tp.IsTournamentOwner))
    def non_participants(self, request, pk=None):
        get_object_or_404(self.queryset, pk=pk)
        serializer = pls.PlayerSerializer(plm.Player.objects.exclude(participations__tournament=pk), many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True, permission_classes=(
            permissions.IsAuthenticated,
            tp.IsTournamentOwner))
    def participants(self, request, pk=None):
        get_object_or_404(self.queryset, pk=pk)
        serializer = pls.PlayerSerializer(
            plm.Player.objects.filter(participations__tournament=pk, participations__is_qualified=True), many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        tournament = serializer.save()
        ta = tm.TournamentAdmin(user=self.request.user, tournament=tournament, is_master=True)
        ta.save()

    @action(methods=['get'], detail=True, permission_classes=(
            permissions.IsAuthenticated,
            tp.IsTournamentOwner))
    def admins(self, request, pk=None):
        get_object_or_404(self.queryset, pk=pk)
        serializer = ts.TournamentAdminSerializer(tm.TournamentAdmin.objects.filter(tournament=pk), many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True, permission_classes=(
            permissions.IsAuthenticated,
            tp.IsTournamentOwner))
    def non_admins(self, request, pk=None):
        get_object_or_404(self.queryset, pk=pk)
        serializer = MinimalUserSerializer(User.objects.exclude(tournaments__tournament=pk), many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True)
    def teams(self, request, pk=None):
        get_object_or_404(self.queryset, pk=pk)
        serializer = tes.TeamSerializer(
            tem.Team.objects.filter(tournament=pk), many=True)
        return Response(serializer.data)

    @action(
        methods=['get'],
        detail=True,
        url_name='group_phases')
    def group_phases(self, request, pk=None):
        get_object_or_404(self.queryset, pk=pk)
        serializer = GroupPhaseSerializer(gpm.GroupPhase.objects.filter(tournament=pk), many=True)
        return Response(serializer.data)

    @action(
        methods=['get'],
        detail=True,
        url_name='cup_phases')
    def cup_phases(self, request, pk=None):
        get_object_or_404(self.queryset, pk=pk)
        serializer = cps.CupPhaseSerializer(cpm.CupPhase.objects.filter(tournament=pk), many=True)
        return Response(serializer.data)

    @action(
        methods=['get'],
        detail=True,
        url_name='not_assigned',
        permission_classes=[
            permissions.IsAuthenticated,
            tp.IsTournamentAdmin
        ]
    )
    def not_assigned(self, request, pk=None):
        players = plm.Player.objects.filter(participations__tournament=pk, participations__is_qualified=True).exclude(
            team_member__team__tournament=pk)
        serializer = pls.ShallowPlayerSerializer(players, many=True)
        return Response(serializer.data)
