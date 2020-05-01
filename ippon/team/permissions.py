from rest_framework import permissions

import ippon.models.team as tem
import ippon.utils.permissions as ip


class IsTeamOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            pk = view.kwargs["pk"]
            team = tem.Team.objects.get(pk=pk)
            return ip.is_user_admin_of_the_tournament(request, team.tournament)
        except (KeyError, tem.Team.DoesNotExist):
            return False

    def has_object_permission(self, request, view, team):
        return ip.is_user_admin_of_the_tournament(request, team.tournament)
