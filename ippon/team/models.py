from django.db import models

import ippon.player.models as plm
import ippon.tournament.models as tm
import ippon.team.models as tem


class Team(models.Model):
    name = models.CharField(max_length=100, blank=False)
    tournament = models.ForeignKey(tm.Tournament, related_name='teams', on_delete=models.CASCADE)

    def get_member_ids(self):
        members = TeamMember.objects.filter(team__pk=self.id)
        return [player.id for player in plm.Player.objects.filter(pk__in=[member.player.id for member in members])]


class TeamMember(models.Model):
    player = models.ForeignKey(plm.Player, on_delete=models.CASCADE, related_name='team_member')
    team = models.ForeignKey(tem.Team, related_name='team_members', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('player', 'team')
