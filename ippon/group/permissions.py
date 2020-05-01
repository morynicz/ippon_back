from rest_framework import permissions

from ippon.group.serializers import GroupSerializer
from ippon.models import Group, GroupPhase
from ippon.permissions import is_user_admin_of_the_tournament, has_object_creation_permission


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