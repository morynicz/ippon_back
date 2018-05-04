from rest_framework import permissions

from ippon.models import ClubAdmin


class IsClubAdminOrReadOnlyClub(permissions.BasePermission):

    def has_object_permission(self, request, view, club):
        if request and request.method in permissions.SAFE_METHODS:
            return True
        return ClubAdmin.objects.all().filter(user=request.user, club=club)


class IsClubAdminOrReadOnlyDependent(permissions.BasePermission):
    def has_object_permission(self, request, view, player):
        if request and request.method in permissions.SAFE_METHODS:
            return True
        return ClubAdmin.objects.all().filter(user=request.user, club=player.club)