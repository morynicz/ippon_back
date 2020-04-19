import datetime
from math import floor

from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver

import ippon.player.models as plm


class TournamentAdmin(models.Model):
    tournament = models.ForeignKey('Tournament', related_name='admins', on_delete=models.CASCADE)
    user = models.ForeignKey('auth.User', related_name='tournaments', on_delete=models.PROTECT)
    is_master = models.BooleanField()

    def get_user(self):
        return {'id': self.user.id, 'username': self.user.username}


class TournamentParticipation(models.Model):
    tournament = models.ForeignKey('Tournament', related_name='participations', on_delete=models.PROTECT)
    player = models.ForeignKey('Player', related_name='participations', on_delete=models.PROTECT)
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


class Team(models.Model):
    name = models.CharField(max_length=100, blank=False)
    tournament = models.ForeignKey('Tournament', related_name='teams', on_delete=models.CASCADE)

    def get_member_ids(self):
        members = TeamMember.objects.filter(team__pk=self.id)
        return [player.id for player in plm.Player.objects.filter(pk__in=[member.player.id for member in members])]


class TeamMember(models.Model):
    player = models.ForeignKey('Player', on_delete=models.CASCADE, related_name='team_member')
    team = models.ForeignKey('Team', related_name='team_members', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('player', 'team')


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
    tournament = models.ForeignKey('Tournament', related_name='team_fights', on_delete=models.PROTECT)
    aka_team = models.ForeignKey('Team', on_delete=models.PROTECT, related_name='+')
    shiro_team = models.ForeignKey('Team', on_delete=models.PROTECT, related_name='+')
    winner = models.IntegerField(choices=WINNER, default=0)
    status = models.IntegerField(choices=STATUS, default=0)

    def __str__(self):
        return "TeamFight {{id: {id}, aka_team: {aka}, shiro_team: {shiro}, winner: {win} }}".format(id=self.id,
                                                                                                     aka=self.aka_team,
                                                                                                     shiro=self.shiro_team,
                                                                                                     win=self.winner)

    def get_teams_points(self, team):
        return Point.objects.filter(player__team_member__team=team, fight__team_fight=self).exclude(type=4).count()

    def get_aka_points(self):
        return self.get_teams_points(self.aka_team)

    def get_aka_wins(self):
        return self.fights.filter(winner=1).count()

    def get_shiro_points(self):
        return self.get_teams_points(self.shiro_team)

    def get_shiro_wins(self):
        return self.fights.filter(winner=2).count()


class Fight(models.Model):
    aka = models.ForeignKey('Player', on_delete=models.CASCADE, related_name='+')
    shiro = models.ForeignKey('Player', on_delete=models.CASCADE, related_name='+')
    team_fight = models.ForeignKey('TeamFight', on_delete=models.CASCADE, related_name='fights')
    ordering_number = models.IntegerField(default=0)
    winner = models.IntegerField(choices=WINNER, default=0)
    status = models.IntegerField(choices=STATUS, default=0)


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
    player = models.ForeignKey('Player', on_delete=models.PROTECT, related_name='points')
    fight = models.ForeignKey('Fight', on_delete=models.PROTECT, related_name='points')
    type = models.IntegerField(choices=POINT_TYPE)


class Location(models.Model):
    tournament = models.ForeignKey('Tournament', related_name='locations', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=False)


class GroupPhase(models.Model):
    tournament = models.ForeignKey('Tournament', related_name='group_phases', on_delete=models.CASCADE)
    fight_length = models.IntegerField()
    name = models.CharField(max_length=100, blank=False)


class Group(models.Model):
    name = models.CharField(max_length=100, blank=False)
    group_phase = models.ForeignKey('GroupPhase', related_name='groups', on_delete=models.PROTECT)


class GroupMember(models.Model):
    group = models.ForeignKey('Group', related_name='group_members', on_delete=models.PROTECT)
    team = models.ForeignKey('Team', related_name='group_member', on_delete=models.PROTECT)


class GroupFight(models.Model):
    group = models.ForeignKey('Group', related_name='group_fights', on_delete=models.PROTECT)
    team_fight = models.ForeignKey('TeamFight', related_name='group_fight', on_delete=models.CASCADE)

    def __str__(self):
        return "group: {}\nteam_fight: {}".format(self.group, self.team_fight)

    def delete(self, using=None, keep_parents=False):
        super(GroupFight, self).delete()
        self.team_fight.delete()


class CupPhase(models.Model):
    tournament = models.ForeignKey('Tournament', related_name='cup_phases', on_delete=models.PROTECT)
    fight_length = models.IntegerField()
    final_fight_length = models.IntegerField()
    name = models.CharField(max_length=100, blank=False)
    number_of_positions = models.IntegerField(default=2)


class NoSuchFightException(Exception):
    pass


class CupFight(models.Model):
    cup_phase = models.ForeignKey('CupPhase', related_name='cup_fights', on_delete=models.PROTECT)
    team_fight = models.ForeignKey('TeamFight', related_name='cup_fight', on_delete=models.SET_NULL, null=True)
    previous_shiro_fight = models.OneToOneField('self', on_delete=models.CASCADE, related_name='+', null=True)
    previous_aka_fight = models.OneToOneField('self', on_delete=models.CASCADE, related_name='+', null=True)

    def get_following_fight(self):
        try:
            return CupFight.objects.get(Q(previous_aka_fight=self) | Q(previous_shiro_fight=self))
        except CupFight.DoesNotExist:
            raise NoSuchFightException()

    def delete(self, using=None, keep_parents=False):
        super(CupFight, self).delete()
        if self.team_fight:
            self.team_fight.delete()

    def __str__(self):
        return "CupFight {{id: {id}, cup_phase: {cup_phase}, team_fight: {team_fight}, previous_shiro: {previous_shiro}, previous_aka: {previous_aka} }}".format(
            id=self.id,
            team_fight=self.team_fight,
            cup_phase=self.cup_phase,
            previous_aka=self.previous_aka_fight.id if self.previous_aka_fight is not None else None,
            previous_shiro=self.previous_shiro_fight.id if self.previous_shiro_fight is not None else None
        )


@receiver(post_save, sender=TeamFight)
def winner_change_handler(sender, **kwargs):
    try:
        cup_fight = CupFight.objects.get(team_fight=kwargs['instance'].id)
        parent = cup_fight.get_following_fight()
        sibling = parent.previous_aka_fight if parent.previous_aka_fight.id is not cup_fight.id else parent.previous_shiro_fight
        if sibling.team_fight.winner is not 0:
            tournament = parent.cup_phase.tournament
            if (parent.team_fight is None):
                parent.team_fight = tournament.team_fights.create(aka_team=get_winner(parent.previous_aka_fight),
                                                                  shiro_team=get_winner(parent.previous_shiro_fight))
                parent.save()
            else:
                if parent.previous_aka_fight.id is cup_fight.id:
                    parent.team_fight.aka_team = get_winner(cup_fight)
                else:
                    parent.team_fight.shiro_team = get_winner(cup_fight)
                parent.team_fight.save()

    except (CupFight.DoesNotExist, NoSuchFightException):
        return


def get_winner(cup_fight):
    team_fight = cup_fight.team_fight
    return team_fight.aka_team if team_fight.winner is 1 else team_fight.shiro_team


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

    event = models.ForeignKey("Event", on_delete=models.CASCADE, null=True)
