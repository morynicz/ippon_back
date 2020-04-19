import datetime

import django
from django.db import IntegrityError
from django.test import TestCase

import ippon.fight.models
import ippon.models
import ippon.team_fight.models as tfm
from ippon.models import NoSuchFightException
import ippon.tournament.models as tm
import ippon.player.models as plm
import ippon.club.models as cl


class TestCupFights(TestCase):
    def setUp(self):
        self.tournament = tm.Tournament.objects.create(
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
        with self.assertRaises(NoSuchFightException):
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

    def test_cup_fight_when_winner_is_set_and_sibling_has_winner_already_set_creates_team_fight_in_parent(self):
        self.cf_aka.team_fight.winner = 1
        self.cf_aka.team_fight.save()
        self.cup_fight.team_fight.winner = 2
        self.cup_fight.team_fight.save()
        self.cf_parent.refresh_from_db()
        self.assertIsNotNone(self.cf_parent.team_fight)
        self.assertEqual(self.cf_parent.team_fight.aka_team, self.t3)
        self.assertEqual(self.cf_parent.team_fight.shiro_team, self.t2)

    def test_when_aka_fight_winner_is_set_and_shiro_sibling_doesnt_have_winner_yet_doesnt_change_parent(self):
        self.cf_aka.team_fight.winner = 1
        self.cf_aka.team_fight.save()
        self.cf_parent.refresh_from_db()
        self.assertIsNone(self.cf_parent.team_fight)

    def test_when_shiro_fight_winner_is_set_and_aka_sibling_doesnt_have_winner_yet_doesnt_change_parent(self):
        self.cup_fight.team_fight.winner = 1
        self.cup_fight.team_fight.save()
        self.cf_parent.refresh_from_db()
        self.assertIsNone(self.cf_parent.team_fight)

    def test_when_shiro_fight_winner_is_changed_and_parent_was_laready_created_but_still_in_prep_change_parent(self):
        self.cf_aka.team_fight.winner = 1
        self.cf_aka.team_fight.save()
        self.cup_fight.team_fight.winner = 2
        self.cup_fight.team_fight.save()
        self.cf_parent.refresh_from_db()
        old_parent_tf_id = self.cf_parent.team_fight.id
        self.cf_aka.team_fight.winner = 2
        self.cf_aka.team_fight.save()
        self.cf_parent.refresh_from_db()
        current_parent_tf = self.cf_parent.team_fight

        self.assertEqual(old_parent_tf_id, current_parent_tf.id)
        self.assertEqual(current_parent_tf.aka_team, self.t4)
        self.assertEqual(current_parent_tf.shiro_team, self.t2)


class CupPhaseTests(TestCase):
    def setUp(self) -> None:
        self.tournament = tm.Tournament.objects.create(
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
        c = cl.Club.objects.create(
            name='cn1',
            webpage='http://cw1.co',
            description='cd1',
            city='cc1')
        self.cup_phase = self.tournament.cup_phases.create(name="CP",
                                                           fight_length=3,
                                                           final_fight_length=5)
        self.t1 = self.tournament.teams.create(name='t1')
        self.t2 = self.tournament.teams.create(name='t2')
        self.team_fight1 = self.tournament.team_fights.create(aka_team=self.t1,
                                                              shiro_team=self.t2)
        self.cf1 = self.cup_phase.cup_fights.create(team_fight=self.team_fight1)

        self.p1 = plm.Player.objects.create(name='pn1', surname='ps1', rank=7,
                                            birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=c)
        self.p2 = plm.Player.objects.create(name='pn2', surname='ps2', rank=7,
                                            birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=c)
        self.p3 = plm.Player.objects.create(name='pn3', surname='ps3', rank=7,
                                            birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=c)
        self.p4 = plm.Player.objects.create(name='pn4', surname='ps4', rank=7,
                                            birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=c)
        self.p5 = plm.Player.objects.create(name='pn5', surname='ps5', rank=7,
                                            birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=c)
        self.p6 = plm.Player.objects.create(name='pn6', surname='ps6', rank=7,
                                            birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=c)
        self.p7 = plm.Player.objects.create(name='pn7', surname='ps6', rank=7,
                                            birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=c)
        self.p8 = plm.Player.objects.create(name='pn8', surname='ps6', rank=7,
                                            birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=c)

        self.t1.team_members.create(player=self.p1)
        self.t1.team_members.create(player=self.p2)
        self.t1.team_members.create(player=self.p3)
        self.t1.team_members.create(player=self.p7)

        self.t2.team_members.create(player=self.p4)
        self.t2.team_members.create(player=self.p5)
        self.t2.team_members.create(player=self.p6)
        self.t2.team_members.create(player=self.p8)

        self.f1 = self.team_fight1.fights.create(aka=self.p1, shiro=self.p4)
        self.f2 = self.team_fight1.fights.create(aka=self.p2, shiro=self.p5)
        self.f3 = self.team_fight1.fights.create(aka=self.p3, shiro=self.p6)
        self.f4 = self.team_fight1.fights.create(aka=self.p7, shiro=self.p8)

    def test_destruction_of_cup_phase_is_impossible_when_there_are_some_fights_in_it(self):
        with self.assertRaises(django.db.models.ProtectedError) as pe:
            self.cup_phase.delete()
        self.assertTrue(tfm.TeamFight.objects.filter(cup_fight=self.cf1).count())
        self.assertTrue(ippon.models.CupFight.objects.filter(cup_phase=self.cup_phase).count())
        self.assertTrue(ippon.models.Fight.objects.filter(team_fight=self.team_fight1).count())
