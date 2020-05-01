from rest_framework import permissions

from ippon.cup_fight.serializers import CupFightSerializer
from ippon.models import CupPhase
from ippon.utils.permissions import has_object_creation_permission, is_user_admin_of_the_tournament


class IsCupFightOwnerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == "POST":
            return has_object_creation_permission(request, CupFightSerializer, "cup_phase",
                                                  CupPhase)
        return True

    def has_object_permission(self, request, view, cup_fight):
        if request and request.method in permissions.SAFE_METHODS:
            return True
        return is_user_admin_of_the_tournament(request, cup_fight.cup_phase.tournament)