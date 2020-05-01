from rest_framework import viewsets, permissions

import ippon.models
from ippon.cup_fight.serializers import CupFightSerializer
from ippon.cup_fight.permissions import IsCupFightOwnerOrReadOnly


class CupFightViewSet(viewsets.ModelViewSet):
    queryset = ippon.models.cup_fight.CupFight.objects.all()
    serializer_class = CupFightSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsCupFightOwnerOrReadOnly)