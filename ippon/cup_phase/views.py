from rest_framework import viewsets, permissions
from rest_framework.decorators import action, api_view
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

import ippon.models
from ippon.authorization_views import has_tournament_authorization
from ippon.cup_phase.serializers import CupPhaseSerializer
from ippon.models import CupPhase
from ippon.serializers import CupFightSerializer
from ippon.tournament import permissions as tp


class CupPhaseViewSet(viewsets.ModelViewSet):
    queryset = CupPhase.objects.all()
    serializer_class = CupPhaseSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          tp.IsTournamentAdminOrReadOnlyDependent)

    @action(
        methods=['get'],
        detail=True,
        url_name='cup_fights')
    def cup_fights(self, request, pk=None):
        get_object_or_404(self.queryset, pk=pk)
        serializer = CupFightSerializer(ippon.models.cup_fight.CupFight.objects.filter(cup_phase=pk), many=True)
        return Response(serializer.data)


@api_view(['GET'])
def cup_phase_authorization(request, pk, format=None):
    cup_phase = get_object_or_404(CupPhase.objects.all(), pk=pk)
    return has_tournament_authorization([True, False], cup_phase.tournament.id, request)