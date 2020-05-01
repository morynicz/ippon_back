from rest_framework import viewsets, permissions
from rest_framework.decorators import action, api_view
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from ippon.authorization_views import has_tournament_authorization
from ippon.models import GroupPhase, Group
from ippon.group.serializers import GroupSerializer
from ippon.group_phase.serializers import GroupPhaseSerializer
from ippon.tournament import permissions as tp


class GroupPhaseViewSet(viewsets.ModelViewSet):
    queryset = GroupPhase.objects.all()
    serializer_class = GroupPhaseSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          tp.IsTournamentAdminOrReadOnlyDependent)

    @action(
        methods=['get'],
        detail=True,
        url_name='groups')
    def groups(self, request, pk=None):
        get_object_or_404(self.queryset, pk=pk)
        serializer = GroupSerializer(Group.objects.filter(group_phase=pk), many=True)
        return Response(serializer.data)


@api_view(['GET'])
def group_phase_authorization(request, pk, format=None):
    group_phase = get_object_or_404(GroupPhase.objects.all(), pk=pk)
    return has_tournament_authorization([True, False], group_phase.tournament.id, request)