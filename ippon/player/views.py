from rest_framework import viewsets, permissions, generics
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404

import ippon.club.authorizations as ca
import ippon.club.permissisons as clp
import ippon.models.player as plm
import ippon.player.serializers as pls


class PlayerViewSet(viewsets.ModelViewSet):
    queryset = plm.Player.objects.all()
    serializer_class = pls.PlayerSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          clp.IsClubAdminOrReadOnlyDependent)


class ShallowPlayerListView(generics.ListAPIView):
    queryset = plm.Player.objects.all()
    serializer_class = pls.ShallowPlayerSerializer


class ShallowPlayerDetailView(generics.RetrieveAPIView):
    queryset = plm.Player.objects.all()
    serializer_class = pls.ShallowPlayerSerializer


@api_view(['GET'])
def player_authorization(request, pk, format=None):
    player = get_object_or_404(plm.Player.objects.all(), pk=pk)
    return ca.has_club_authorization(player.club_id, request)
