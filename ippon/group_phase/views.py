from rest_framework import viewsets, permissions
from rest_framework.decorators import action, api_view
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

import ippon.tournament.authorizations as ta
import ippon.models.group_phase as gpm
import ippon.models.group as gm
import ippon.group.serializers as gs
import ippon.group_phase.serializers as gps
import ippon.tournament.permissions as tp


class GroupPhaseViewSet(viewsets.ModelViewSet):
    queryset = gpm.GroupPhase.objects.all()
    serializer_class = gps.GroupPhaseSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          tp.IsTournamentAdminOrReadOnlyDependent)

    @action(
        methods=['get'],
        detail=True,
        url_name='groups')
    def groups(self, request, pk=None):
        get_object_or_404(self.queryset, pk=pk)
        serializer = gs.GroupSerializer(gm.Group.objects.filter(group_phase=pk), many=True)
        return Response(serializer.data)


@api_view(['GET'])
def group_phase_authorization(request, pk, format=None):
    group_phase = get_object_or_404(gpm.GroupPhase.objects.all(), pk=pk)
    return ta.has_tournament_authorization([True, False], group_phase.tournament.id, request)
