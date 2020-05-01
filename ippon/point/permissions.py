from rest_framework import permissions

import ippon.models
import ippon.models.fight
import ippon.permissions as ip
import ippon.point.serializers as pts
import ippon.models.tournament as tm


class IsPointOwnerOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method == "POST":
            return ip.has_object_creation_permission(request, pts.PointSerializer, "fight", ippon.models.fight.Fight,
                                                     ip.get_tournament_from_fight)
        return True

    def has_object_permission(self, request, view, point):
        if request and request.method in permissions.SAFE_METHODS:
            return True
        return tm.TournamentAdmin.objects.filter(tournament=point.fight.team_fight.tournament,
                                                 user=request.user).count() > 0
