from rest_framework import permissions, viewsets

import ippon.models.point as ptm
import ippon.point.permissions as ptp
import ippon.point.serializers as pts


class PointViewSet(viewsets.ModelViewSet):
    queryset = ptm.Point.objects.all()
    serializer_class = pts.PointSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        ptp.IsPointOwnerOrReadOnly,
    )
