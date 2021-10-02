from rest_framework import permissions

import ippon.cup_fight.serializers as cfs
import ippon.models.cup_phase as cpm
import ippon.utils.permissions as iup


class IsCupFightOwnerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == "POST":
            return iup.has_object_creation_permission(
                request, cfs.CupFightSerializer, "cup_phase", cpm.CupPhase
            )
        return True

    def has_object_permission(self, request, view, cup_fight):
        if request and request.method in permissions.SAFE_METHODS:
            return True
        return iup.is_user_admin_of_the_tournament(
            request, cup_fight.cup_phase.tournament
        )
