import datetime

from django.db import IntegrityError
from django.test import TestCase

import ippon.models
from ippon import models
from ippon.models import Club, Team, Player, NoSuchFightException, Tournament


class TournamentParticipationTests(TestCase):
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

class TestTeamFights(TestCase):
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
        c = Club.objects.create(
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
        self.p1 = Player.objects.create(name='pn1', surname='ps1', rank=7,
                                        birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=c)
        self.p2 = Player.objects.create(name='pn2', surname='ps2', rank=7,
                                        birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=c)
        self.p3 = Player.objects.create(name='pn3', surname='ps3', rank=7,
                                        birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=c)
        self.p4 = Player.objects.create(name='pn4', surname='ps4', rank=7,
                                        birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=c)
        self.p5 = Player.objects.create(name='pn5', surname='ps5', rank=7,
                                        birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=c)
        self.p6 = Player.objects.create(name='pn6', surname='ps6', rank=7,
                                        birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=c)
        self.p7 = Player.objects.create(name='pn7', surname='ps6', rank=7,
                                        birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=c)
        self.p8 = Player.objects.create(name='pn8', surname='ps6', rank=7,
                                        birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=c)

        self.t1.team_members.create(player=self.p1)
        self.t1.team_members.create(player=self.p2)
        self.t1.team_members.create(player=self.p3)
        self.t1.team_members.create(player=self.p7)

        self.t2.team_members.create(player=self.p4)
        self.t2.team_members.create(player=self.p5)
        self.t2.team_members.create(player=self.p6)
        self.t2.team_members.create(player=self.p8)

        f1 = self.team_fight1.fights.create(aka=self.p1, shiro=self.p4)
        f1.points.create(player=self.p1, type=0)
        f1.points.create(player=self.p4, type=1)
        f1.points.create(player=self.p1, type=2)
        f1.winner = 1
        f1.save()

        f2 = self.team_fight1.fights.create(aka=self.p2, shiro=self.p5)
        f2.points.create(player=self.p5, type=3)
        f2.points.create(player=self.p2, type=1)
        f2.status = 2
        f2.save()

        f3 = self.team_fight1.fights.create(aka=self.p3, shiro=self.p6)
        f3.points.create(player=self.p3, type=4)
        f3.points.create(player=self.p3, type=4)
        f3.points.create(player=self.p6, type=5)
        f3.points.create(player=self.p3, type=1)
        f3.points.create(player=self.p3, type=1)
        f3.winner = 1
        f3.save()

        f4 = self.team_fight1.fights.create(aka=self.p7, shiro=self.p8)
        f4.points.create(player=self.p8, type=4)
        f4.points.create(player=self.p8, type=4)
        f4.winner = 2
        f4.save()


    def test_correctly_counts_aka_wins(self):
        self.assertEqual(self.team_fight1.get_aka_wins(), 2)

    def test_correctly_counts_aka_points(self):
        self.assertEqual(self.team_fight1.get_aka_points(), 5)

    def test_correctly_counts_shiro_wins(self):
        self.assertEqual(self.team_fight1.get_shiro_wins(), 1)

    def test_correctly_counts_shiro_points(self):
        self.assertEqual(self.team_fight1.get_shiro_points(), 3)
