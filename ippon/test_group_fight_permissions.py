import datetime
import unittest

import django.test
from django.contrib.auth.models import User

from ippon.models import Club, Tournament, Team, Player, TeamFight, TournamentAdmin, GroupPhase, Group
from ippon.permissions import IsGroupFightOwnerOrReadOnly


class TestGroupFightPermissions(django.test.TestCase):
    def setUp(self):
        c = Club.objects.create(
            name='cn1',
            webpage='http://cw1.co',
            description='cd1',
            city='cc1')
        self.admin = User.objects.create(username='admin', password='password')
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
        self.t2 = Team.objects.create(tournament=self.to, name='t2')
        self.p2 = Player.objects.create(name='pn2', surname='ps2', rank=7,
                                        birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=c)
        self.t2.team_members.create(player=self.p2)

        self.tf = TeamFight.objects.create(aka_team=self.t1, shiro_team=self.t2, tournament=self.to)
        self.fight = self.tf.fights.create(aka=self.p1, shiro=self.p2)
        self.permission = IsGroupFightOwnerOrReadOnly()
        self.request = unittest.mock.Mock()
        self.view = unittest.mock.Mock()
        self.request.user = self.admin
        self.group_phase = GroupPhase.objects.create(name="gp", tournament=self.to, fight_length=3)
        self.group = Group.objects.create(name="g1", group_phase=self.group_phase)


class TestGroupFightPermissionNotAdmin(TestGroupFightPermissions):
    def setUp(self):
        super(TestGroupFightPermissionNotAdmin, self).setUp()

    def test_permits_when_safe_method(self):
        self.request.method = 'GET'
        result = self.permission.has_object_permission(self.request, self.view, self.fight)
        self.assertEqual(result, True)

    def test_doesnt_permit_when_unsafe_method(self):
        self.request.method = 'PUT'
        result = self.permission.has_object_permission(self.request, self.view, self.fight)
        self.assertEqual(result, False)


class TestGroupFightPermissionAdmin(TestGroupFightPermissions):
    def setUp(self):
        super(TestGroupFightPermissionAdmin, self).setUp()
        TournamentAdmin.objects.create(user=self.admin, tournament=self.to, is_master=False)

    def test_permits_when_safe_method(self):
        self.request.method = 'GET'
        result = self.permission.has_object_permission(self.request, self.view, self.fight)
        self.assertEqual(result, True)

    def test_doesnt_permit_when_unsafe_method(self):
        self.request.method = 'PUT'
        result = self.permission.has_object_permission(self.request, self.view, self.fight)
        self.assertEqual(result, True)
