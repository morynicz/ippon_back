from django.db import models

import ippon.models.player as plm

POINT_TYPE = [
    (0, 'Men'),
    (1, 'Kote'),
    (2, 'Do'),
    (3, 'Tsuki'),
    (4, 'Foul'),
    (5, 'Hansoku'),
    (6, 'Other')
]


class Point(models.Model):
    player = models.ForeignKey(plm.Player, on_delete=models.PROTECT, related_name='points')
    fight = models.ForeignKey('Fight', on_delete=models.PROTECT, related_name='points')
    type = models.IntegerField(choices=POINT_TYPE)
