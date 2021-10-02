from django.db import models


class GroupPhase(models.Model):
    tournament = models.ForeignKey(
        "Tournament", related_name="group_phases", on_delete=models.CASCADE
    )
    fight_length = models.IntegerField()
    name = models.CharField(max_length=100, blank=False)
