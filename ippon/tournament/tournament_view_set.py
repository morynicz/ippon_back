from django.contrib.auth.models import User
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from ippon.models import TournamentParticipation, Player, TournamentAdmin, Team, GroupPhase, CupPhase
from ippon.tournament.tournament import Tournament
from ippon.permissions import IsTournamentAdminOrReadOnlyTournament, IsTournamentOwner
from ippon.serializers import TournamentParticipationSerializer, PlayerSerializer, \
    TournamentAdminSerializer, MinimalUserSerializer, TeamSerializer, GroupPhaseSerializer, CupPhaseSerializer
from ippon.tournament.serializers import TournamentSerializer


class TournamentViewSet(viewsets.ModelViewSet):
    queryset = Tournament.objects.all()
    serializer_class = TournamentSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsTournamentAdminOrReadOnlyTournament)

    @action(methods=['get'], detail=True, permission_classes=[
        permissions.IsAuthenticated,
        IsTournamentOwner])
    def participations(self, request, pk=None):
        get_object_or_404(self.queryset, pk=pk)
        serializer = TournamentParticipationSerializer(TournamentParticipation.objects.filter(tournament=pk), many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True, permission_classes=[
        permissions.IsAuthenticated,
        IsTournamentOwner])
    def non_participants(self, request, pk=None):
        get_object_or_404(self.queryset, pk=pk)
        serializer = PlayerSerializer(Player.objects.exclude(participations__tournament=pk), many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True, permission_classes=[
        permissions.IsAuthenticated,
        IsTournamentOwner])
    def participants(self, request, pk=None):
        get_object_or_404(self.queryset, pk=pk)
        serializer = PlayerSerializer(
            Player.objects.filter(participations__tournament=pk, participations__is_qualified=True), many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        tournament = serializer.save()
        ta = TournamentAdmin(user=self.request.user, tournament=tournament, is_master=True)
        ta.save()

    @action(methods=['get'], detail=True, permission_classes=[
        permissions.IsAuthenticated,
        IsTournamentOwner])
    def admins(self, request, pk=None):
        get_object_or_404(self.queryset, pk=pk)
        serializer = TournamentAdminSerializer(TournamentAdmin.objects.filter(tournament=pk), many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True, permission_classes=[
        permissions.IsAuthenticated,
        IsTournamentOwner])
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