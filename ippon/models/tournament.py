import datetime
from math import floor

from django.db import models

import ippon.models.player as plm
import ippon.models.event as em


class TournamentAdmin(models.Model):
    tournament = models.ForeignKey('Tournament', related_name='admins', on_delete=models.CASCADE)
    user = models.ForeignKey('auth.User', related_name='tournaments', on_delete=models.PROTECT)
    is_master = models.BooleanField()

    def get_user(self):
        return {'id': self.user.id, 'username': self.user.username}


class TournamentParticipation(models.Model):
    tournament = models.ForeignKey('Tournament', related_name='participations', on_delete=models.PROTECT)
    player = models.ForeignKey(plm.Player, related_name='participations', on_delete=models.PROTECT)
    is_paid = models.BooleanField(default=False)
    is_registered = models.BooleanField(default=False)
    is_qualified = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    def check_is_age_ok(self):
        delta = self.tournament.date - self.player.birthday
        pa = floor(delta / datetime.timedelta(days=365))
        ta = self.tournament.age_constraint_value
        return is_numeric_constraint_satisfied(pa, self.tournament.age_constraint, ta)

    def check_is_rank_ok(self):
        return is_numeric_constraint_satisfied(self.player.rank, self.tournament.rank_constraint,
                                               self.tournament.rank_constraint_value)

    def check_is_sex_ok(self):
        constraints = {
            0: True,
            1: self.player.sex == 1,
            2: self.player.sex == 0
        }
        return constraints[self.tournament.sex_constraint]


def is_numeric_constraint_satisfied(lhs, constraint, rhs):
    constraints = {
        0: True,
        1: (lhs < rhs),
        2: (lhs <= rhs),
        3: (lhs > rhs),
        4: (lhs >= rhs),
        5: (lhs == rhs),
        6: (lhs != rhs)
    }
    return constraints[constraint]


NUMERIC_CONSTRAINT = [
    (0, 'None'),
    (1, 'Less'),
    (2, 'LessOrEqual'),
    (3, 'Greater'),
    (4, 'GreateOrEqual'),
    (5, 'Equal'),
    (6, 'NotEqual')
]
SEX_CONSTRAINT = [
    (0, 'None'),
    (1, 'WomenOnly'),
    (2, 'MenOnly')
]


class Tournament(models.Model):
    name = models.CharField(max_length=100, blank=False)
    webpage = models.URLField()
    description = models.TextField()
    city = models.CharField(max_length=100, blank=False)
    date = models.DateField()
    address = models.CharField(max_length=500, blank=False)
    team_size = models.IntegerField()
    group_match_length = models.IntegerField()
    ko_match_length = models.IntegerField()
    final_match_length = models.IntegerField()
    age_constraint = models.IntegerField(choices=NUMERIC_CONSTRAINT)
    rank_constraint = models.IntegerField(choices=NUMERIC_CONSTRAINT)
    sex_constraint = models.IntegerField(choices=SEX_CONSTRAINT)
    rank_constraint_value = models.IntegerField(choices=plm.RANK_CHOICES)
    age_constraint_value = models.IntegerField()
    finals_depth = models.IntegerField()

    event = models.ForeignKey(em.Event, on_delete=models.CASCADE, null=True)
