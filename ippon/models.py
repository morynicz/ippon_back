from django.db import models


class Club(models.Model):
    name = models.CharField(max_length=100, blank=False)
    webpage = models.URLField()
    description = models.TextField()
    city = models.CharField(max_length=100, blank=False)


SEX_CHOICES = [
    (0, 'Male'),
    (1, 'Female')
]

RANK_CHOICES = [
    (0, 'None'),
    (1, 'Kyu_6'),
    (2, 'Kyu_5'),
    (3, 'Kyu_4'),
    (4, 'Kyu_3'),
    (5, 'Kyu_2'),
    (6, 'Kyu_1'),
    (7, 'Dan_1'),
    (8, 'Dan_2'),
    (9, 'Dan_3'),
    (10, 'Dan_4'),
    (11, 'Dan_5'),
    (12, 'Dan_6'),
    (13, 'Dan_7'),
    (14, 'Dan_8')
]


class Player(models.Model):
    sex = models.IntegerField(choices=SEX_CHOICES)
    rank = models.IntegerField(choices=RANK_CHOICES)
    name = models.CharField(max_length=100, blank=False)
    surname = models.CharField(max_length=100, blank=False)
    birthday = models.DateField()
    club_id = models.ForeignKey('Club', related_name='players', on_delete=models.PROTECT)


class ClubAdmin(models.Model):
    club = models.ForeignKey('Club', related_name='admins', on_delete=models.PROTECT)
    user = models.ForeignKey('auth.User', related_name='clubs', on_delete=models.PROTECT)


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


class TournamentAdmin(models.Model):
    tournament = models.ForeignKey('Tournament', related_name='admins', on_delete=models.PROTECT)
    user = models.ForeignKey('auth.User', related_name='tournaments', on_delete=models.PROTECT)
    is_master = models.BooleanField()


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
