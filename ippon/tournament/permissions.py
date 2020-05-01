import json

from rest_framework import permissions

import ippon.models.tournament as tm
from ippon.permissions import is_user_admin_of_the_tournament


class IsTournamentAdminOrReadOnlyTournament(permissions.BasePermission):

    def has_object_permission(self, request, view, tournament):
        if request and request.method in permissions.SAFE_METHODS:
            return True
        return tm.TournamentAdmin.objects.all().filter(user=request.user, tournament=tournament).count() > 0


class IsTournamentAdminOrReadOnlyDependent(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == "POST":
            try:
                return is_user_admin_of_the_tournament(request, request.data["tournament"])
            except(KeyError):
                return False
        return True

    def has_object_permission(self, request, view, dependent):
        if request and request.method in permissions.SAFE_METHODS:
            return True
        return tm.TournamentAdmin.objects.all().filter(user=request.user, tournament=dependent.tournament).count() > 0


class IsTournamentAdminDependent(permissions.BasePermission):
    def has_object_permission(self, request, view, dependent):
        return tm.TournamentAdmin.objects.all().filter(user=request.user, tournament=dependent.tournament)


class IsTournamentOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            tournament = tm.Tournament.objects.get(pk=(view.kwargs["pk"]))
            return tm.TournamentAdmin.objects.filter(user=request.user, tournament=tournament,
                                                     is_master=True).count() > 0
        except KeyError:
            return False
        except tm.Tournament.DoesNotExist:
            return True

    def has_object_permission(self, request, view, admin):
        return tm.TournamentAdmin.objects.filter(user=request.user, tournament=admin.tournament,
                                                 is_master=True).count() > 0


class IsTournamentOwnerAdminCreation(permissions.BasePermission):
    def has_permission(self, request, view):  # TODO: CCheck if this is needed
        try:
            req_body = json.loads(request.body)
            return tm.TournamentAdmin.objects.filter(user=request.user, tournament=req_body["tournament_id"],
                                                     is_master=True).exists()
        except KeyError:
            return False

    def has_object_permission(self, request, view, admin):
        return tm.TournamentAdmin.objects.filter(user=request.user, tournament=admin.tournament,
                                                 is_master=True).exists()


class IsTournamentAdminParticipantCreation(permissions.BasePermission):
    def has_permission(self, request, view):  # TODO: CCheck if this is needed
        try:
            req_body = json.loads(request.body)
            return tm.TournamentAdmin.objects.filter(user=request.user, tournament=req_body["tournament_id"]).exists()
        except KeyError:
            return False

    def has_object_permission(self, request, view, admin):
        return tm.TournamentAdmin.objects.filter(user=request.user, tournament=admin.tournament).exists()


class IsTournamentAdmin(permissions.BasePermission):
    def has_permission(self, request, view) -> bool:
        try:
            pk = view.kwargs["pk"]
            tournament = tm.Tournament.objects.get(pk=pk)
            return is_user_admin_of_the_tournament(request, tournament)
        except (KeyError, tm.Tournament.DoesNotExist):
            return False
