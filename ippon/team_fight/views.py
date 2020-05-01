from rest_framework import viewsets, permissions
from rest_framework.decorators import action, api_view
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

import ippon.models.fight as fm
import ippon.fight.serializers as fs
import ippon.models.team_fight as tfm
import ippon.team_fight.serializers as tfs
import ippon.tournament.permissions as tp
from ippon.tournament.authorizations import has_tournament_authorization
from ippon.models import team_fight as tfm


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
        serializer = fs.FightSerializer(fm.Fight.objects.filter(team_fight=team_fight), many=True)
        return Response(serializer.data)


@api_view(['GET'])
def team_fight_authorization(request, pk, format=None):
    team_fight = tfm.TeamFight.objects.get(pk=pk)
    return has_tournament_authorization([True, False], team_fight.tournament.id, request)