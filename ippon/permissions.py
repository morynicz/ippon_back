from rest_framework import permissions

from ippon.models import ClubAdmin, TournamentAdmin, CupPhase, Group, GroupPhase, TeamFight, Team, Fight, Tournament
from ippon.serializers import CupFightSerializer, GroupFightSerializer, GroupSerializer, FightSerializer, \
    PointSerializer


def is_user_admin_of_the_tournament(request, tournament):
    return TournamentAdmin.objects.filter(tournament=tournament,
                                          user=request.user).count() > 0


def get_tournament_from_dependent(obj):
    return obj.tournament


def has_object_creation_permission(request, serializer, tournament_dependent_class_field,
                                   tournament_dependent_class, getter_fcn=get_tournament_from_dependent):
    try:
        serializer = serializer(data=request.data)
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
    def has_permission(self, request, view):
        return ClubAdmin.objects.filter(user=request.user, club=view.kwargs["pk"]).count() > 0

    def has_object_permission(self, request, view, admin):
        return ClubAdmin.objects.filter(user=request.user, club=admin.club).count() > 0


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
                serializer=GroupFightSerializer,
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
