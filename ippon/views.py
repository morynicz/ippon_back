from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, action
from rest_framework.response import Response

from ippon.models import Player, Club, ClubAdmin, Tournament, TournamentAdmin
from ippon.permissions import IsClubAdminOrReadOnlyClub, IsClubAdminOrReadOnlyDependent, \
    IsTournamentAdminOrReadOnlyTournament
from ippon.serializers import PlayerSerializer, ClubSerializer, TournamentSerializer


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

    def perform_create(self, serializer):
        tournament = serializer.save()
        ta = TournamentAdmin(user=self.request.user, tournament=tournament)
        ta.save()


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
