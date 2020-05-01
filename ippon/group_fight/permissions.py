from rest_framework import permissions

import ippon.group_fight.serializers as gfs
import ippon.models.group as gm
import ippon.utils.permissions as iup


class IsGroupFightOwnerOrReadOnly(permissions.BasePermission):
    def get_tournament(self, group):
        return group.group_phase.tournament

    def has_permission(self, request, view):
        if request.method == "POST":
            return iup.has_object_creation_permission(
                request=request,
                serializer_class=gfs.GroupFightSerializer,
                tournament_dependent_class_field="group",
                tournament_dependent_class=gm.Group,
                getter_fcn=self.get_tournament)
        return True

    def has_object_permission(self, request, view, group_fight):
        if request and request.method in permissions.SAFE_METHODS:
            return True
        return iup.is_user_admin_of_the_tournament(request, group_fight.team_fight.tournament)
