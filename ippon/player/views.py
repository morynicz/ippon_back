from rest_framework import viewsets, permissions, generics
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404

from ippon.club.authorizations import has_club_authorization
from ippon.club import permissisons as clp
import ippon.player.serializers as pls
import ippon.models.player as plm
from ippon.models import player as plm


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
    return has_club_authorization(player.club_id, request)