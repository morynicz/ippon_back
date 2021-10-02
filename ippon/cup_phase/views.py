from rest_framework import permissions, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

import ippon.cup_fight.serializers as cfs
import ippon.cup_phase.serializers as cps
import ippon.models.cup_fight as cfm
import ippon.models.cup_phase as cpm
import ippon.tournament.authorizations as ta
import ippon.tournament.permissions as tp


class CupPhaseViewSet(viewsets.ModelViewSet):
    queryset = cpm.CupPhase.objects.all()
    serializer_class = cps.CupPhaseSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        tp.IsTournamentAdminOrReadOnlyDependent,
    )

    @action(methods=["get"], detail=True, url_name="cup_fights")
    def cup_fights(self, request, pk=None):
        get_object_or_404(self.queryset, pk=pk)
        serializer = cfs.CupFightSerializer(cfm.CupFight.objects.filter(cup_phase=pk), many=True)
        return Response(serializer.data)


@api_view(["GET"])
def cup_phase_authorization(request, pk, format=None):
    cup_phase = get_object_or_404(cpm.CupPhase.objects.all(), pk=pk)
    return ta.has_tournament_authorization([True, False], cup_phase.tournament.id, request)
