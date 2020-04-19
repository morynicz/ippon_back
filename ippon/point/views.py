from rest_framework import viewsets, permissions

import ippon.point.models as ptm
import ippon.point.permissions as ptp
import ippon.point.serializers as pts


class PointViewSet(viewsets.ModelViewSet):
    queryset = ptm.Point.objects.all()
    serializer_class = pts.PointSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          ptp.IsPointOwnerOrReadOnly)
