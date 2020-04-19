from django.contrib.auth.models import User
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

import ippon.club.models as cl
from ippon.models import Player
from ippon.club.permissisons import IsClubAdminOrReadOnlyClub, IsClubOwner, IsClubOwnerAdminCreation
from ippon.serializers import PlayerSerializer, MinimalUserSerializer
from ippon.club.serializers import ClubSerializer, ClubAdminSerializer


class ClubViewSet(viewsets.ModelViewSet):
    queryset = cl.Club.objects.all()
    serializer_class = ClubSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsClubAdminOrReadOnlyClub)

    def perform_create(self, serializer):
        club = serializer.save()
        ca = cl.ClubAdmin(user=self.request.user, club=club)
        ca.save()

    @action(methods=['get'], detail=True)
    def players(self, request, pk=None):
        serializer = PlayerSerializer(Player.objects.filter(club_id=pk), many=True)
        return Response(serializer.data)

    @action(methods=['get'],
            detail=True,
            permission_classes=(permissions.IsAuthenticated, IsClubOwner))
    def admins(self, request, pk=None):
        serializer = ClubAdminSerializer(cl.ClubAdmin.objects.filter(club=pk), many=True)
        return Response(serializer.data)

    @action(methods=['get'],
            detail=True,
            permission_classes=(permissions.IsAuthenticated, IsClubOwner))
    def non_admins(self, request, pk=None):
        serializer = MinimalUserSerializer(User.objects.exclude(clubs__club=pk), many=True)
        return Response(serializer.data)


class ClubAdminViewSet(viewsets.ModelViewSet):
    queryset = cl.ClubAdmin.objects.all()
    serializer_class = ClubAdminSerializer
    permission_classes = (permissions.IsAuthenticated,
                          IsClubOwnerAdminCreation)