from django.views.generic.base import View
from rest_framework import permissions
from rest_framework.request import Request

from ippon.models import CupPhase, Group
import ippon.models.tournament as tm

from ippon.event_models import Event, EventAdmin
from ippon.serializers import CupFightSerializer, GroupFightSerializer


def is_user_admin_of_the_tournament(request, tournament):
    return tm.TournamentAdmin.objects.filter(tournament=tournament,
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


def get_tournament_from_fight(fight):
    return fight.team_fight.tournament


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
            try:
                return any([i.user == request.user for i in EventAdmin.objects.filter(event=Event.objects.get(pk=pk))])
            except Exception:
                return False
