from rest_framework import viewsets, permissions, generics

from ippon.club import permissisons as clp
import ippon.player.serializers as pls
import ippon.player.models as plm


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
