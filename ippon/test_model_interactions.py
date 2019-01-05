import datetime

from django.test import TestCase

import ippon.models
from ippon import models


class TournamentDependentClasses(TestCase):
    def setUp(self):
        self.tournament = ippon.models.Tournament.objects.create(
            name='T1',
            webpage='http://w1.co',
            description='d1',
            city='c1',
            date=datetime.date(year=2021, month=1, day=1),
            address='a1',
            team_size=1,
            group_match_length=3,
            ko_match_length=3,
            final_match_length=3,
            finals_depth=0,
            age_constraint=5,
            age_constraint_value=20,
            rank_constraint=5,
            rank_constraint_value=7,
            sex_constraint=1)
        self.tournament.save()
        self.cup_phase = self.tournament.cup_phases.create(name="CP",
                                                           fight_length=3,
                                                           final_fight_length=5)
        self.t1 = self.tournament.teams.create(name='t1')
        self.t2 = self.tournament.teams.create(name='t2')
        self.team_fight = self.tournament.team_fights.create(aka_team=self.t1,
                                                             shiro_team=self.t2)


class GroupFightAndTeamFightInteractionTests(TournamentDependentClasses):
    def setUp(self):
        super(GroupFightAndTeamFightInteractionTests, self).setUp()
        self.group_phase = self.tournament.group_phases.create(name="a", fight_length=4)
        self.group = self.group_phase.groups.create(name="aa")
        self.group_fight = self.group.group_fights.create(team_fight=self.team_fight)

    def test_group_fight_deletion_triggers_underlying_team_fight_deletion(self):
        self.group_fight.delete()
        with self.assertRaises(models.TeamFight.DoesNotExist):
            print(models.TeamFight.objects.get(pk=self.team_fight.id))

    def test_team_fight_deletion_triggers_related_group_fight_deletion(self):
        self.team_fight.delete()
        with self.assertRaises(models.GroupFight.DoesNotExist):
            print(models.GroupFight.objects.get(pk=self.group_fight.id))
