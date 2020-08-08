from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

import ippon.event.permissions as ep
import ippon.event.serializers as es
import ippon.models.event as em


class EventViewSet(viewsets.ModelViewSet):
    queryset = em.Event.objects.all()
    serializer_class = es.EventSerializer
    permission_classes = [ep.IsEventOwnerOrReadOnly]

    def create(self, request: Request, *args, **kwargs) -> Response:
        res = super(EventViewSet, self).create(request, *args, **kwargs)
        admin = em.EventAdmin(
            user=request.user,
            event=em.Event.objects.get(pk=res.data['id'])
        )
        admin.save()
        return res

    @action(
        methods=["GET"],
        detail=False,
        url_name='my_tournaments')
    def return_users_events(self, request: Request):
        if request.user.is_authenticated:
            events = [i.event for i in em.EventAdmin.objects.filter(user=request.user)]
            return Response(data=self.serializer_class(events, many=True, context={'request': request}).data)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data={"error": "You are not logged in."})
