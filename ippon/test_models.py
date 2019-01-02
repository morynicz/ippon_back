import datetime

from django.db import IntegrityError
from django.test import TestCase

import ippon.tournament.tournament
from ippon import models
from ippon.models import Club, Team, Player, NoSuchFightException
from ippon.tournament.tournament import Tournament


class TournamentParticipationTests(TestCase):
    def setUp(self):
        self.tournament = ippon.tournament.tournament.Tournament.objects.create(
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
        c = models.Club.objects.create(
            name='cn1',
            webpage='http://cw1.co',
            description='cd1',
            city='cc1')
        c.save()
        p = models.Player.objects.create(
            name='pn1',
            surname='ps1',
            rank=7,
            birthday=datetime.date(year=2001, month=1, day=1),
            sex=1,
            club_id=c
        )
        p.save()

        self.part = models.TournamentParticipation.objects.create(
            tournament=self.tournament,
            player=p
        )

    def test_is_age_ok_true_when_age_is_equal_and_constraint_is_equal(self):
        self.assertTrue(self.part.check_is_age_ok())

    def test_is_age_ok_false_when_age_is_equal_and_constraint_is_not_equal(self):
        self.tournament.age_constraint = 6
        self.assertFalse(self.part.check_is_age_ok())

    def test_is_rank_ok_false_when_rank_is_equal_and_constrint_is_not_equal(self):
        self.assertTrue(self.part.check_is_rank_ok())

    def test_is_rank_ok_false_when_rank_is_equal_and_constraint_is_not_equal(self):
        self.tournament.rank_constraint = 6
        self.assertFalse(self.part.check_is_rank_ok())

    def test_is_sex_ok_true_when_female_and_woman_only(self):
        self.assertTrue(self.part.check_is_sex_ok())

    def test_is_sex_ok_false_when_female_and_man_only(self):
        self.tournament.sex_constraint = 2
        self.assertFalse(self.part.check_is_sex_ok())


class TeamTests(TestCase):
    def test_player_and_team_combinations_are_unique(self):
        c = Club.objects.create(
            name='cn1',
            webpage='http://cw1.co',
            description='cd1',
            city='cc1')
        self.to = Tournament.objects.create(name='T1', webpage='http://w1.co', description='d1', city='c1',
                                            date=datetime.date(year=2021, month=1, day=1), address='a1',
                                            team_size=1, group_match_length=3, ko_match_length=3,
                                            final_match_length=3, finals_depth=0, age_constraint=5,
                                            age_constraint_value=20, rank_constraint=5, rank_constraint_value=7,
                                            sex_constraint=1)
        self.t1 = Team.objects.create(tournament=self.to, name='t1')
        self.p1 = Player.objects.create(name='pn1', surname='ps1', rank=7,
                                        birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=c)
        self.t1.team_members.create(player=self.p1)

        with self.assertRaises(IntegrityError):
            self.t1.team_members.create(player=self.p1)


class TestCupFights(TestCase):
    def setUp(self):
        self.tournament = ippon.tournament.tournament.Tournament.objects.create(
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
        self.team_fight1 = self.tournament.team_fights.create(aka_team=self.t1,
                                                              shiro_team=self.t2)
        self.cup_fight = self.cup_phase.cup_fights.create(team_fight=self.team_fight1)


class CupFightFollowingFightTests(TestCupFights):
    def setUp(self):
        super(CupFightFollowingFightTests, self).setUp()

    def test_fight_throws_no_such_fight_when_het_following_called_on_final(self):
        with self.assertRaises(NoSuchFightException) as ex:
            self.cup_fight.get_following_fight()

    def test_cup_fight_which_is_previous_on_aka_side_returns_following_fight(self):
        following_aka = self.cup_phase.cup_fights.create(team_fight=self.team_fight1, previous_aka_fight=self.cup_fight)
        self.assertEqual(self.cup_fight.get_following_fight(), following_aka)


class CupFightSiblingTests(TestCupFights):
    def setUp(self):
        super(CupFightSiblingTests, self).setUp()
        self.t3 = self.tournament.teams.create(name='t3')
        self.t4 = self.tournament.teams.create(name='t4')
        self.tf_aka = self.tournament.team_fights.create(aka_team=self.t3,
                                                         shiro_team=self.t4)
        self.cf_aka = self.cup_phase.cup_fights.create(team_fight=self.tf_aka)
        self.cf_parent = self.cup_phase.cup_fights.create(previous_aka_fight=self.cf_aka,
                                                          previous_shiro_fight=self.cup_fight)
        self.cf_aka.team_fight.winner = 1
        self.cf_aka.team_fight.save()

        self.cup_phase.cup_fights.create()

    def test_cup_fight_when_winner_is_set_and_sibling_has_winner_already_set_creates_team_fight_in_parent(self):
        self.cup_fight.team_fight.winner = 2
        self.cup_fight.team_fight.save()
        self.cf_parent.refresh_from_db()
        self.assertIsNotNone(self.cf_parent.team_fight)
        self.assertEqual(self.cf_parent.team_fight.aka_team, self.t3)
        self.assertEqual(self.cf_parent.team_fight.shiro_team, self.t2)

    def test_when_fight_winner_is_set_and_sibling_doesnt_have_winner_yet_doesnt_change_parent(self):
        self.assertIsNone(self.cf_parent.team_fight)
