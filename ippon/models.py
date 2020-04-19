from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver

import ippon.team_fight.models as tfm
from ippon.player import models as plm

from ippon.player.models import Player
from ippon.club.models import Club, ClubAdmin
from ippon.tournament.models import Tournament, TournamentAdmin, TournamentParticipation
from ippon.team.models import Team, TeamMember
from ippon.team_fight.models import TeamFight, WINNER, STATUS


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


@receiver(post_save, sender=tfm.TeamFight)
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


class NoSuchFightException(Exception):
    pass


class Fight(models.Model):
    aka = models.ForeignKey(plm.Player, on_delete=models.CASCADE, related_name='+')
    shiro = models.ForeignKey(plm.Player, on_delete=models.CASCADE, related_name='+')
    team_fight = models.ForeignKey('TeamFight', on_delete=models.CASCADE, related_name='fights')
    ordering_number = models.IntegerField(default=0)
    winner = models.IntegerField(choices=WINNER, default=0)
    status = models.IntegerField(choices=STATUS, default=0)
