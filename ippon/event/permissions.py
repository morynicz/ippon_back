from django.views.generic.base import View
from rest_framework import permissions
from rest_framework.request import Request

import ippon.models.event as em


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
                return any(
                    [i.user == request.user for i in em.EventAdmin.objects.filter(event=em.Event.objects.get(pk=pk))]
                )
            except Exception:
                return False
