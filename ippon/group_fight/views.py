from rest_framework import viewsets, permissions

import ippon.group_fight.permissions as gfp
import ippon.group_fight.serializers as gfs
import ippon.models.group_fight as gfm


class GroupFightViewSet(viewsets.ModelViewSet):
    queryset = gfm.GroupFight.objects.all()
    serializer_class = gfs.GroupFightSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          gfp.IsGroupFightOwnerOrReadOnly)