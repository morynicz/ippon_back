from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from ippon.models import Event, EventAdmin
from ippon.event.permissions import IsEventOwnerOrReadOnly
from ippon.event.serializers import EventSerializer


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsEventOwnerOrReadOnly]

    def create(self, request: Request, *args, **kwargs) -> Response:
        res = super(EventViewSet, self).create(request, *args, **kwargs)
        admin = EventAdmin(
            user=request.user,
            event=Event.objects.get(pk=res.data['id'])
        )
        admin.save()
        return res

    @action(
        methods=["GET"],
        detail=False,
        url_name='my_tournaments')
    def my_tournaments(self, request: Request):
        if request.user.is_authenticated:
            model = Event.objects.filter(event_owner=request.user.pk)
            return Response(data=self.serializer_class(model, many=True).data)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data={"error": "You are not logged in."})