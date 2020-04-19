import datetime

from django.test.testcases import TestCase

from ippon.club import models as cl
from ippon.player import models as plm
from ippon.tournament import models as tm


class TestTeamFights(TestCase):
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