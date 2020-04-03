import json

from django.views.generic.base import View
from rest_framework import permissions
from rest_framework.request import Request

from ippon.models import ClubAdmin, TournamentAdmin, CupPhase, Group, GroupPhase, TeamFight, Team, Fight, Tournament, \
    Club, Event
from ippon.serializers import CupFightSerializer, GroupFightSerializer, GroupSerializer, FightSerializer, \
    PointSerializer, PlayerSerializer


def is_user_admin_of_the_tournament(request, tournament):
    return TournamentAdmin.objects.filter(tournament=tournament,
                                          user=request.user).count() > 0


def get_tournament_from_dependent(obj):
    return obj.tournament


def has_object_creation_permission(request, serializer_class, tournament_dependent_class_field,
                                   tournament_dependent_class, getter_fcn=get_tournament_from_dependent):
    try:
        serializer = serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        tournament_dependent = tournament_dependent_class.objects.get(
            pk=serializer.validated_data[tournament_dependent_class_field].id)
        return is_user_admin_of_the_tournament(request, getter_fcn(tournament_dependent))
    except(KeyError):
        return False
    except tournament_dependent_class.DoesNotExist:
        return False


class IsClubAdminOrReadOnlyClub(permissions.BasePermission):
    def has_object_permission(self, request, view, club):
        if request and request.method in permissions.SAFE_METHODS:
            return True
        return ClubAdmin.objects.all().filter(user=request.user, club=club).count() > 0


class IsClubAdminOrReadOnlyDependent(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == "POST":
            try:
                serializer = PlayerSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                club = serializer.validated_data["club_id"].id
                return ClubAdmin.objects.all().filter(user=request.user, club=club).count() > 0
            except Club.DoesNotExist:
                return False
        return True

    def has_object_permission(self, request, view, player):
        if request and request.method in permissions.SAFE_METHODS:
            return True
        return ClubAdmin.objects.all().filter(user=request.user, club=player.club_id).count() > 0


class IsTournamentAdminOrReadOnlyTournament(permissions.BasePermission):

    def has_object_permission(self, request, view, tournament):
        if request and request.method in permissions.SAFE_METHODS:
            return True
        return TournamentAdmin.objects.all().filter(user=request.user, tournament=tournament).count() > 0


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
        return TournamentAdmin.objects.all().filter(user=request.user, tournament=dependent.tournament).count() > 0


class IsTournamentAdminDependent(permissions.BasePermission):
    def has_object_permission(self, request, view, dependent):
        return TournamentAdmin.objects.all().filter(user=request.user, tournament=dependent.tournament)


class IsTournamentOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            tournament = Tournament.objects.get(pk=(view.kwargs["pk"]))
            return TournamentAdmin.objects.filter(user=request.user, tournament=tournament,
                                                  is_master=True).count() > 0
        except KeyError:
            return False
        except Tournament.DoesNotExist:
            return True

    def has_object_permission(self, request, view, admin):
        return TournamentAdmin.objects.filter(user=request.user, tournament=admin.tournament,
                                              is_master=True).count() > 0


class IsClubOwner(permissions.BasePermission):
    def has_permission(self, request, view):  # TODO: CCheck if this is needed
        try:
            return ClubAdmin.objects.filter(user=request.user, club=view.kwargs["pk"]).count() > 0
        except KeyError:
            return False

    def has_object_permission(self, request, view, admin):
        return ClubAdmin.objects.filter(user=request.user, club=admin.club).count() > 0


class IsClubOwnerAdminCreation(permissions.BasePermission):
    def has_permission(self, request, view):  # TODO: CCheck if this is needed
        try:
            req_body = json.loads(request.body)
            return ClubAdmin.objects.filter(user=request.user, club=req_body["club_id"]).count() > 0
        except KeyError:
            return False

    def has_object_permission(self, request, view, admin):
        return ClubAdmin.objects.filter(user=request.user, club=admin.club).count() > 0


class IsTournamentOwnerAdminCreation(permissions.BasePermission):
    def has_permission(self, request, view):  # TODO: CCheck if this is needed
        try:
            req_body = json.loads(request.body)
            return TournamentAdmin.objects.filter(user=request.user, tournament=req_body["tournament_id"],
                                                  is_master=True).exists()
        except KeyError:
            return False

    def has_object_permission(self, request, view, admin):
        return TournamentAdmin.objects.filter(user=request.user, tournament=admin.tournament, is_master=True).exists()


class IsTournamentAdminParticipantCreation(permissions.BasePermission):
    def has_permission(self, request, view):  # TODO: CCheck if this is needed
        try:
            req_body = json.loads(request.body)
            return TournamentAdmin.objects.filter(user=request.user, tournament=req_body["tournament_id"]).exists()
        except KeyError:
            return False

    def has_object_permission(self, request, view, admin):
        return TournamentAdmin.objects.filter(user=request.user, tournament=admin.tournament).exists()


def get_tournament_from_fight(fight):
    return fight.team_fight.tournament


class IsPointOwnerOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method == "POST":
            return has_object_creation_permission(request, PointSerializer, "fight", Fight, get_tournament_from_fight)
        return True

    def has_object_permission(self, request, view, point):
        if request and request.method in permissions.SAFE_METHODS:
            return True
        return TournamentAdmin.objects.filter(tournament=point.fight.team_fight.tournament,
                                              user=request.user).count() > 0


class IsFightOwnerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == "POST":
            return has_object_creation_permission(request, FightSerializer, "team_fight", TeamFight)
        return True

    def has_object_permission(self, request, view, fight):
        if request and request.method in permissions.SAFE_METHODS:
            return True
        return TournamentAdmin.objects.filter(tournament=fight.team_fight.tournament, user=request.user).count() > 0


class IsGroupOwnerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == "POST":
            if "pk" in view.kwargs:
                try:
                    group = Group.objects.get(pk=view.kwargs["pk"])
                    return is_user_admin_of_the_tournament(request, group.group_phase.tournament)
                except Group.DoesNotExist:
                    return False
            return has_object_creation_permission(request, GroupSerializer, "group_phase", GroupPhase)
        return True

    def has_object_permission(self, request, view, group):
        if request and request.method in permissions.SAFE_METHODS:
            return True
        return is_user_admin_of_the_tournament(request, group.group_phase.tournament)


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


class IsGroupOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            pk = view.kwargs["pk"]
            group = Group.objects.get(pk=pk)
            return is_user_admin_of_the_tournament(request, group.group_phase.tournament)
        except (KeyError, Group.DoesNotExist):
            return False

    def has_object_permission(self, request, view, group):
        return is_user_admin_of_the_tournament(request, group.group_phase.tournament)


class IsTeamOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            pk = view.kwargs["pk"]
            team = Team.objects.get(pk=pk)
            return is_user_admin_of_the_tournament(request, team.tournament)
        except (KeyError, Team.DoesNotExist):
            return False

    def has_object_permission(self, request, view, team):
        return is_user_admin_of_the_tournament(request, team.tournament)


class IsTournamentAdmin(permissions.BasePermission):
    def has_permission(self, request, view) -> bool:
        try:
            pk = view.kwargs["pk"]
            tournament = Tournament.objects.get(pk=pk)
            return is_user_admin_of_the_tournament(request, tournament)
        except (KeyError, Tournament.DoesNotExist):
            return False


class IsEventOwnerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request: Request, view: View) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True
        elif request.method == "POST":
            try:
                return request.user.pk == int(request.data["event_owner"])
            except (KeyError, ValueError):
                return False
        else:
            pk = view.kwargs["pk"]
            if request.user == Event.objects.get(pk=pk).event_owner:
                return True
            else:
                return False
