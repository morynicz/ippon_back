from django.db import models


class CupPhase(models.Model):
    tournament = models.ForeignKey('Tournament', related_name='cup_phases', on_delete=models.PROTECT)
    fight_length = models.IntegerField()
    final_fight_length = models.IntegerField()
    name = models.CharField(max_length=100, blank=False)
    number_of_positions = models.IntegerField(default=2)