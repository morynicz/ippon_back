from rest_framework import viewsets, permissions

import ippon.models
from ippon.group_fight.permissions import IsGroupFightOwnerOrReadOnly
from ippon.group_fight.serializers import GroupFightSerializer


class GroupFightViewSet(viewsets.ModelViewSet):
    queryset = ippon.models.group_fight.GroupFight.objects.all()
    serializer_class = GroupFightSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsGroupFightOwnerOrReadOnly)