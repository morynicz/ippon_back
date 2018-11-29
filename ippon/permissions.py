from rest_framework import permissions

from ippon.models import ClubAdmin, TournamentAdmin


class IsClubAdminOrReadOnlyClub(permissions.BasePermission):
    def has_object_permission(self, request, view, club):
        if request and request.method in permissions.SAFE_METHODS:
            return True
        return ClubAdmin.objects.all().filter(user=request.user, club=club)


class IsClubAdminOrReadOnlyDependent(permissions.BasePermission):
    def has_object_permission(self, request, view, player):
        if request and request.method in permissions.SAFE_METHODS:
            return True
        return ClubAdmin.objects.all().filter(user=request.user, club=player.club_id)


class IsTournamentAdminOrReadOnlyTournament(permissions.BasePermission):
    def has_object_permission(self, request, view, tournament):
        if request and request.method in permissions.SAFE_METHODS:
            return True
        return TournamentAdmin.objects.all().filter(user=request.user, tournament=tournament)


class IsTournamentAdminOrReadOnlyDependent(permissions.BasePermission):
    def has_object_permission(self, request, view, dependent):
        if request and request.method in permissions.SAFE_METHODS:
            return True
        return TournamentAdmin.objects.all().filter(user=request.user, tournament=dependent.tournament)


class IsTournamentAdminDependent(permissions.BasePermission):
    def has_object_permission(self, request, view, dependent):
        return TournamentAdmin.objects.all().filter(user=request.user, tournament=dependent.tournament)


class IsTournamentOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, admin):
        return TournamentAdmin.objects.filter(user=request.user, tournament=admin.tournament, is_master=True)


class IsClubOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, admin):
        return ClubAdmin.objects.filter(user=request.user, club=admin.club)


class IsPointOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, point):
        if request and request.method in permissions.SAFE_METHODS:
            return True
        return TournamentAdmin.objects.filter(tournament=point.fight.team_fight.tournament,
                                              user=request.user).count() > 0


class IsFightOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, fight):
        if request and request.method in permissions.SAFE_METHODS:
            return True
        return TournamentAdmin.objects.filter(tournament=fight.team_fight.tournament, user=request.user).count() > 0


class IsGroupOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, group):
        if request and request.method in permissions.SAFE_METHODS:
            return True
        return TournamentAdmin.objects.filter(tournament=group.group_phase.tournament, user=request.user).count() > 0


class IsGroupFightOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, group_fight):
        if request and request.method in permissions.SAFE_METHODS:
            return True
        return TournamentAdmin.objects.filter(tournament=group_fight.team_fight.tournament,
                                              user=request.user).count() > 0
