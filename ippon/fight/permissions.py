from rest_framework import permissions

import ippon.fight.serializers as fs
import ippon.permissions as ip
import ippon.models.team_fight as tfm
import ippon.models.tournament as tm


class IsFightOwnerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == "POST":
            return ip.has_object_creation_permission(request, fs.FightSerializer, "team_fight", tfm.TeamFight)
        return True

    def has_object_permission(self, request, view, fight):
        if request and request.method in permissions.SAFE_METHODS:
            return True
        return tm.TournamentAdmin.objects.filter(tournament=fight.team_fight.tournament, user=request.user).count() > 0
