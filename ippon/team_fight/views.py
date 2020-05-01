from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from ippon.models import Fight
import ippon.fight.serializers as fs
import ippon.models.team_fight as tfm
import ippon.team_fight.serializers as tfs
import ippon.tournament.permissions as tp


class TeamFightViewSet(viewsets.ModelViewSet):
    queryset = tfm.TeamFight.objects.all()
    serializer_class = tfs.TeamFightSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          tp.IsTournamentAdminOrReadOnlyDependent)

    @action(
        methods=['get'],
        detail=True,
        url_name='fights')
    def fights(self, request, pk=None):
        team_fight = get_object_or_404(self.queryset, pk=pk)
        serializer = fs.FightSerializer(Fight.objects.filter(team_fight=team_fight), many=True)
        return Response(serializer.data)
