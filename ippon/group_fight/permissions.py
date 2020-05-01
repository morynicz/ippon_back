from rest_framework import permissions

from ippon.group_fight.serializers import GroupFightSerializer
from ippon.models import Group
from ippon.permissions import has_object_creation_permission, is_user_admin_of_the_tournament


class IsGroupFightOwnerOrReadOnly(permissions.BasePermission):
    def get_tournament(self, group):
        return group.group_phase.tournament

    def has_permission(self, request, view):
        if request.method == "POST":
            return has_object_creation_permission(
                request=request,
                serializer_class=GroupFightSerializer,
                tournament_dependent_class_field="group",
                tournament_dependent_class=Group,
                getter_fcn=self.get_tournament)
        return True

    def has_object_permission(self, request, view, group_fight):
        if request and request.method in permissions.SAFE_METHODS:
            return True
        return is_user_admin_of_the_tournament(request, group_fight.team_fight.tournament)