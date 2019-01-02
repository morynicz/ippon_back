from django.db import models

from ippon.models import RANK_CHOICES

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
    rank_constraint_value = models.IntegerField(choices=RANK_CHOICES)
    age_constraint_value = models.IntegerField()
    finals_depth = models.IntegerField()