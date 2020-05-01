from rest_framework import permissions

import ippon.group.serializers as gs
import ippon.models.group as gm
import ippon.models.group_phase as gpm
import ippon.utils.permissions as iup


class IsGroupOwnerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == "POST":
            if "pk" in view.kwargs:
                try:
                    group = gm.Group.objects.get(pk=view.kwargs["pk"])
                    return iup.is_user_admin_of_the_tournament(request, group.group_phase.tournament)
                except gm.Group.DoesNotExist:
                    return False
            return iup.has_object_creation_permission(request, gs.GroupSerializer, "group_phase", gpm.GroupPhase)
        return True

    def has_object_permission(self, request, view, group):
        if request and request.method in permissions.SAFE_METHODS:
            return True
        return iup.is_user_admin_of_the_tournament(request, group.group_phase.tournament)


class IsGroupOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            pk = view.kwargs["pk"]
            group = gm.Group.objects.get(pk=pk)
            return iup.is_user_admin_of_the_tournament(request, group.group_phase.tournament)
        except (KeyError, gm.Group.DoesNotExist):
            return False

    def has_object_permission(self, request, view, group):
        return iup.is_user_admin_of_the_tournament(request, group.group_phase.tournament)
