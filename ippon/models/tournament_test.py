import datetime

from django.test.testcases import TestCase

import ippon.models.tournament as tm
import ippon.models.player as plm
import ippon.models.club as clm


class TournamentParticipationTests(TestCase):
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
        c = clm.Club.objects.create(
            name='cn1',
            webpage='http://cw1.co',
            description='cd1',
            city='cc1')
        c.save()
        p = plm.Player.objects.create(
            name='pn1',
            surname='ps1',
            rank=7,
            birthday=datetime.date(year=2001, month=1, day=1),
            sex=1,
            club_id=c
        )
        p.save()

        self.part = tm.TournamentParticipation.objects.create(
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
