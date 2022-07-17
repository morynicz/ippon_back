import datetime
import django.test
import unittest
from django.contrib.auth.models import User

import ippon.fight.permissions as fp
import ippon.fight.serializers as fs
import ippon.models.club as cl
import ippon.models.player as plm
import ippon.models.team as tem
import ippon.models.team_fight as tfm
import ippon.models.tournament as tm


class TestFightPermissions(django.test.TestCase):
    def setUp(self):
        c = cl.Club.objects.create(name="cn1", webpage="http://cw1.co", description="cd1", city="cc1")
        self.admin = User.objects.create(username="admin", password="password")
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
        self.t2 = tem.Team.objects.create(tournament=self.to, name="t2")
        self.p2 = plm.Player.objects.create(
            name="pn2",
            surname="ps2",
            rank=7,
            birthday=datetime.date(year=2001, month=1, day=1),
            sex=1,
            club_id=c,
        )
        self.t2.team_members.create(player=self.p2)

        self.tf = tfm.TeamFight.objects.create(aka_team=self.t1, shiro_team=self.t2, tournament=self.to)
        self.fight = self.tf.fights.create(aka=self.p1, shiro=self.p2)
        self.permission = fp.IsFightOwnerOrReadOnly()
        self.request = unittest.mock.Mock()
        self.view = unittest.mock.Mock()
        self.request.user = self.admin
        self.request.data = fs.FightSerializer(self.fight).data


class TestFightPermissionNotAdmin(TestFightPermissions):
    def setUp(self):
        super(TestFightPermissionNotAdmin, self).setUp()

    def test_permits_when_safe_method(self):
        self.request.method = "GET"
        result = self.permission.has_object_permission(self.request, self.view, self.fight)
        self.assertEqual(result, True)

    def test_doesnt_permit_when_unsafe_method(self):
        self.request.method = "PUT"
        result = self.permission.has_object_permission(self.request, self.view, self.fight)
        self.assertEqual(result, False)

    def test_doesnt_permit_when_post(self):
        self.request.method = "POST"
        result = self.permission.has_permission(self.request, self.view)
        self.assertEqual(result, False)


class TestFightPermissionAdmin(TestFightPermissions):
    def setUp(self):
        super(TestFightPermissionAdmin, self).setUp()
        tm.TournamentAdmin.objects.create(user=self.admin, tournament=self.to, is_master=False)

    def test_permits_when_safe_method(self):
        self.request.method = "GET"
        result = self.permission.has_object_permission(self.request, self.view, self.fight)
        self.assertEqual(result, True)

    def test_doesnt_permit_when_unsafe_method(self):
        self.request.method = "PUT"
        result = self.permission.has_object_permission(self.request, self.view, self.fight)
        self.assertEqual(result, True)

    def test_does_permit_when_post(self):
        self.request.method = "POST"
        result = self.permission.has_permission(self.request, self.view)
        self.assertEqual(result, True)
