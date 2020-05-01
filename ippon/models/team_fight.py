from django.db import models

import ippon.models.point as ptm
import ippon.models.tournament as tm
import ippon.models.team as tem

WINNER = [
    (0, 'None'),
    (1, 'Aka'),
    (2, 'Shiro')
]
STATUS = [
    (0, 'Prepared'),
    (1, 'Started'),
    (2, 'Finished')
]


class TeamFight(models.Model):
    tournament = models.ForeignKey(tm.Tournament, related_name='team_fights', on_delete=models.PROTECT)
    aka_team = models.ForeignKey(tem.Team, on_delete=models.PROTECT, related_name='+')
    shiro_team = models.ForeignKey(tem.Team, on_delete=models.PROTECT, related_name='+')
    winner = models.IntegerField(choices=WINNER, default=0)
    status = models.IntegerField(choices=STATUS, default=0)

    def __str__(self):
        return "TeamFight {{id: {id}, aka_team: {aka}, shiro_team: {shiro}, winner: {win} }}".format(id=self.id,
                                                                                                     aka=self.aka_team,
                                                                                                     shiro=self.shiro_team,
                                                                                                     win=self.winner)

    def get_teams_points(self, team):
        return ptm.Point.objects.filter(player__team_member__team=team, fight__team_fight=self).exclude(type=4).count()

    def get_aka_points(self):
        return self.get_teams_points(self.aka_team)

    def get_aka_wins(self):
        return self.fights.filter(winner=1).count()

    def get_shiro_points(self):
        return self.get_teams_points(self.shiro_team)

    def get_shiro_wins(self):
        return self.fights.filter(winner=2).count()
