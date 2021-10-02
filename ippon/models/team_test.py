import datetime
from django.db.utils import IntegrityError
from django.test.testcases import TestCase

import ippon.models.club as cl
import ippon.models.player as plm
import ippon.models.team as tem
import ippon.models.tournament as tm


class TeamTests(TestCase):
    def test_player_and_team_combinations_are_unique(self):
        c = cl.Club.objects.create(
            name="cn1", webpage="http://cw1.co", description="cd1", city="cc1"
        )
        self.to = tm.Tournament.objects.create(
            name="T1",
            webpage="http://w1.co",
            description="d1",
            city="c1",
            date=datetime.date(year=2021, month=1, day=1),
            address="a1",
            team_size=1,
            group_match_length=3,
            ko_match_length=3,
            final_match_length=3,
            finals_depth=0,
            age_constraint=5,
            age_constraint_value=20,
            rank_constraint=5,
            rank_constraint_value=7,
            sex_constraint=1,
        )
        self.t1 = tem.Team.objects.create(tournament=self.to, name="t1")
        self.p1 = plm.Player.objects.create(
            name="pn1",
            surname="ps1",
            rank=7,
            birthday=datetime.date(year=2001, month=1, day=1),
            sex=1,
            club_id=c,
        )
        self.t1.team_members.create(player=self.p1)

        with self.assertRaises(IntegrityError):
            self.t1.team_members.create(player=self.p1)
