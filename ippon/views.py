from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, action
from rest_framework.response import Response

from ippon.models import Player, Club, ClubAdmin
from ippon.permissions import IsClubAdminOrReadOnlyClub, IsClubAdminOrReadOnlyDependent
from ippon.serializers import PlayerSerializer, ClubSerializer


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
    return Response({
        'isAuthorized': True
    })
