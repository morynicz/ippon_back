from django.contrib.auth.models import User
from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, action
from rest_framework.response import Response

from ippon.models import Player, Club, ClubAdmin, Tournament, TournamentAdmin, TournamentParticipation
from ippon.permissions import IsClubAdminOrReadOnlyClub, IsClubAdminOrReadOnlyDependent, \
    IsTournamentAdminOrReadOnlyTournament, IsTournamentAdminOrReadOnlyDependent, IsTournamentOwner
from ippon.serializers import PlayerSerializer, ClubSerializer, TournamentSerializer, TournamentParticipationSerializer, \
    TournamentAdminSerializer, MinimalUserSerializer


class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsClubAdminOrReadOnlyDependent)


class ClubViewSet(viewsets.ModelViewSet):
    queryset = Club.objects.all()
    serializer_class = ClubSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsClubAdminOrReadOnlyClub)

    def perform_create(self, serializer):
        club = serializer.save()
        print(club)
        ca = ClubAdmin(user=self.request.user, club=club)
        ca.save()

    @action(methods=['get'], detail=True)
    def players(self, request, pk=None):
        serializer = PlayerSerializer(Player.objects.filter(club_id=pk), many=True)
        return Response(serializer.data)


@api_view(['GET'])
def club_authorization(request, pk, format=None):
    try:
        admin = ClubAdmin.objects.get(user=request.user.id, club=pk)
        is_admin = False
        if admin is not None:
            is_admin = True
        return Response({
            'isAuthorized': is_admin
        })

    except ClubAdmin.DoesNotExist:
        return Response({
            'isAuthorized': False
        })


class TournamentViewSet(viewsets.ModelViewSet):
    queryset = Tournament.objects.all()
    serializer_class = TournamentSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsTournamentAdminOrReadOnlyTournament)

    @action(methods=['get'], detail=True)
    def participations(self, request, pk=None):
        serializer = TournamentParticipationSerializer(TournamentParticipation.objects.filter(tournament=pk), many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True)
    def non_participants(self, request, pk=None):
        serializer = PlayerSerializer(Player.objects.exclude(participations__tournament=pk), many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True)
    def participants(self, request, pk=None):
        serializer = PlayerSerializer(
            Player.objects.filter(participations__tournament=pk, participations__is_qualified=True), many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        tournament = serializer.save()
        ta = TournamentAdmin(user=self.request.user, tournament=tournament)
        ta.save()

    @action(methods=['get'], detail=True)
    def admins(self, request, pk=None):
        serializer = TournamentAdminSerializer(TournamentAdmin.objects.filter(tournament=pk), many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True)
    def non_admins(self, request, pk=None):
        serializer = MinimalUserSerializer(User.objects.exclude(tournaments__tournament=pk), many=True)
        return Response(serializer.data)



@api_view(['GET'])
def tournament_staff_authorization(request, pk, format=None):
    return has_tournament_authorization(False, pk, request)


@api_view(['GET'])
def tournament_admin_authorization(request, pk, format=None):
    return has_tournament_authorization(True, pk, request)


def has_tournament_authorization(is_master, pk, request):
    try:
        admin = TournamentAdmin.objects.get(
            user=request.user.id,
            tournament=pk,
            is_master=is_master)
        is_admin = False
        if admin is not None:
            is_admin = True
        return Response({
            'isAuthorized': is_admin
        })

    except TournamentAdmin.DoesNotExist:
        return Response({
            'isAuthorized': False
        })


class TournamentParticipationViewSet(viewsets.ModelViewSet):
    queryset = TournamentParticipation.objects.all()
    serializer_class = TournamentParticipationSerializer
    permission_classes = (permissions.IsAuthenticated,
                          IsTournamentAdminOrReadOnlyDependent)


class TournamentAdminViewSet(viewsets.ModelViewSet):
    queryset = TournamentAdmin.objects.all()
    serializer_class = TournamentAdminSerializer
    permission_classes = (permissions.IsAuthenticated,
                          IsTournamentOwner)

