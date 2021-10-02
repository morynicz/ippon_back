from django.db import models

import ippon.models.player as plm
import ippon.models.team_fight as tfm


class Fight(models.Model):
    aka = models.ForeignKey(plm.Player, on_delete=models.CASCADE, related_name="+")
    shiro = models.ForeignKey(plm.Player, on_delete=models.CASCADE, related_name="+")
    team_fight = models.ForeignKey(
        "TeamFight", on_delete=models.CASCADE, related_name="fights"
    )
    ordering_number = models.IntegerField(default=0)
    winner = models.IntegerField(choices=tfm.WINNER, default=0)
    status = models.IntegerField(choices=tfm.STATUS, default=0)
