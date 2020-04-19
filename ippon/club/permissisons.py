import json

from rest_framework import permissions

import ippon.club.models as cl
import ippon.player.serializers as pls


class IsClubAdminOrReadOnlyClub(permissions.BasePermission):
    def has_object_permission(self, request, view, club):
        if request and request.method in permissions.SAFE_METHODS:
            return True
        return cl.ClubAdmin.objects.all().filter(user=request.user, club=club).count() > 0


class IsClubAdminOrReadOnlyDependent(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == "POST":
            try:
                serializer = pls.PlayerSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                club = serializer.validated_data["club_id"].id
                return cl.ClubAdmin.objects.all().filter(user=request.user, club=club).count() > 0
            except cl.Club.DoesNotExist:
                return False
        return True

    def has_object_permission(self, request, view, player):
        if request and request.method in permissions.SAFE_METHODS:
            return True
        return cl.ClubAdmin.objects.all().filter(user=request.user, club=player.club_id).count() > 0


class IsClubOwner(permissions.BasePermission):
    def has_permission(self, request, view):  # TODO: CCheck if this is needed
        try:
            return cl.ClubAdmin.objects.filter(user=request.user, club=view.kwargs["pk"]).count() > 0
        except KeyError:
            return False

    def has_object_permission(self, request, view, admin):
        return cl.ClubAdmin.objects.filter(user=request.user, club=admin.club).count() > 0


class IsClubOwnerAdminCreation(permissions.BasePermission):
    def has_permission(self, request, view):  # TODO: CCheck if this is needed
        try:
            req_body = json.loads(request.body)
            return cl.ClubAdmin.objects.filter(user=request.user, club=req_body["club_id"]).count() > 0
        except KeyError:
            return False

    def has_object_permission(self, request, view, admin):
        return cl.ClubAdmin.objects.filter(user=request.user, club=admin.club).count() > 0