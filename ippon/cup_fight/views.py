from rest_framework import viewsets, permissions

import ippon.cup_fight.permissions as cfp
import ippon.cup_fight.serializers as cfs
import ippon.models.cup_fight as cfm


class CupFightViewSet(viewsets.ModelViewSet):
    queryset = cfm.CupFight.objects.all()
    serializer_class = cfs.CupFightSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          cfp.IsCupFightOwnerOrReadOnly)
