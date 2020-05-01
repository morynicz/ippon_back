from rest_framework import viewsets, permissions

import ippon.models.cup_fight as cfm
import ippon.cup_fight.serializers as cfs
import ippon.cup_fight.permissions as cfp


class CupFightViewSet(viewsets.ModelViewSet):
    queryset = cfm.CupFight.objects.all()
    serializer_class = cfs.CupFightSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          cfp.IsCupFightOwnerOrReadOnly)
