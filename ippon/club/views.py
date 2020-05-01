from django.contrib.auth.models import User
from rest_framework import viewsets, permissions
from rest_framework.decorators import action, api_view
from rest_framework.response import Response

import ippon.models.club as cl
import ippon.models.player as plm
import ippon.club.permissisons as clp
from ippon.club.authorizations import has_club_authorization
from ippon.user.serailzers import MinimalUserSerializer
import ippon.player.serializers as pls
import ippon.club.serializers as cls


class ClubViewSet(viewsets.ModelViewSet):
    queryset = cl.Club.objects.all()
    serializer_class = cls.ClubSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          clp.IsClubAdminOrReadOnlyClub)

    def perform_create(self, serializer):
        club = serializer.save()
        ca = cl.ClubAdmin(user=self.request.user, club=club)
        ca.save()

    @action(methods=['get'], detail=True)
    def players(self, request, pk=None):
        serializer = pls.PlayerSerializer(plm.Player.objects.filter(club_id=pk), many=True)
        return Response(serializer.data)

    @action(methods=['get'],
            detail=True,
            permission_classes=(permissions.IsAuthenticated, clp.IsClubOwner))
    def admins(self, request, pk=None):
        serializer = cls.ClubAdminSerializer(cl.ClubAdmin.objects.filter(club=pk), many=True)
        return Response(serializer.data)

    @action(methods=['get'],
            detail=True,
            permission_classes=(permissions.IsAuthenticated, clp.IsClubOwner))
    def non_admins(self, request, pk=None):
        serializer = MinimalUserSerializer(User.objects.exclude(clubs__club=pk), many=True)
        return Response(serializer.data)


class ClubAdminViewSet(viewsets.ModelViewSet):
    queryset = cl.ClubAdmin.objects.all()
    serializer_class = cls.ClubAdminSerializer
    permission_classes = (permissions.IsAuthenticated,
                          clp.IsClubOwnerAdminCreation)


@api_view(['GET'])
def club_authorization(request, pk, format=None):
    return has_club_authorization(pk, request)