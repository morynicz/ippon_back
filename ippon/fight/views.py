from rest_framework import viewsets, permissions
from rest_framework.decorators import action, api_view
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

import ippon.fight.serializers as fs
import ippon.fight.permissions as fp
import ippon.models
import ippon.models.fight
import ippon.point.serializers as pts
import ippon.models.point as ptm
import ippon.tournament.authorizations as ta


class FightViewSet(viewsets.ModelViewSet):
    queryset = ippon.models.fight.Fight.objects.all()
    serializer_class = fs.FightSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          fp.IsFightOwnerOrReadOnly)

    @action(
        methods=['get'],
        detail=True,
        url_name='points')
    def points(self, request, pk=None):
        fight = get_object_or_404(self.queryset, pk=pk)
        serializer = pts.PointSerializer(ptm.Point.objects.filter(fight=fight), many=True)
        return Response(serializer.data)


@api_view(['GET'])
def fight_authorization(request, pk, format=None):
    fight = ippon.models.fight.Fight.objects.get(pk=pk)
    return ta.has_tournament_authorization([True, False], fight.team_fight.tournament.id, request)
