import datetime
import unittest

import django.test
from django.contrib.auth.models import User

from ippon.models import GroupPhase, Group
import ippon.models.team_fight as tfm
import ippon.models.team as tem
import ippon.models.tournament as tm
from ippon.group_fight.permissions import IsGroupFightOwnerOrReadOnly
from ippon.group_fight.serializers import GroupFightSerializer


class TestGroupFightPermissions(django.test.TestCase):
    def setUp(self):
        self.admin = User.objects.create(username='admin', password='password')
        self.to = tm.Tournament.objects.create(name='T1', webpage='http://w1.co', description='d1', city='c1',
                                               date=datetime.date(year=2021, month=1, day=1), address='a1',
                                               team_size=1, group_match_length=3, ko_match_length=3,
                                               final_match_length=3, finals_depth=0, age_constraint=5,
                                               age_constraint_value=20, rank_constraint=5, rank_constraint_value=7,
                                               sex_constraint=1)
        self.t1 = tem.Team.objects.create(tournament=self.to, name='t1')
        self.t2 = tem.Team.objects.create(tournament=self.to, name='t2')

        self.tf = tfm.TeamFight.objects.create(aka_team=self.t1, shiro_team=self.t2, tournament=self.to)
        self.permission = IsGroupFightOwnerOrReadOnly()
        self.request = unittest.mock.Mock()
        self.view = unittest.mock.Mock()
        self.request.user = self.admin
        self.group_phase = GroupPhase.objects.create(name="gp", tournament=self.to, fight_length=3)
        self.group = Group.objects.create(name="g1", group_phase=self.group_phase)
        self.group_fight = self.group.group_fights.create(team_fight=self.tf)
        self.request.data = GroupFightSerializer(self.group_fight).data


class TestGroupFightPermissionNotAdmin(TestGroupFightPermissions):
    def setUp(self):
        super(TestGroupFightPermissionNotAdmin, self).setUp()

    def test_permits_when_safe_method(self):
        self.request.method = 'GET'
        result = self.permission.has_object_permission(self.request, self.view, self.group_fight)
        self.assertEqual(result, True)

    def test_doesnt_permit_when_unsafe_method(self):
        self.request.method = 'PUT'
        result = self.permission.has_object_permission(self.request, self.view, self.group_fight)
        self.assertEqual(result, False)

    def test_doesnt_permit_when_post(self):
        self.request.method = 'POST'
        result = self.permission.has_permission(self.request, self.view)
        self.assertEqual(result, False)


class TestGroupFightPermissionAdmin(TestGroupFightPermissions):
    def setUp(self):
        super(TestGroupFightPermissionAdmin, self).setUp()
        tm.TournamentAdmin.objects.create(user=self.admin, tournament=self.to, is_master=False)

    def test_permits_when_safe_method(self):
        self.request.method = 'GET'
        result = self.permission.has_object_permission(self.request, self.view, self.group_fight)
        self.assertEqual(result, True)

    def test_doesnt_permit_when_unsafe_method(self):
        self.request.method = 'PUT'
        result = self.permission.has_object_permission(self.request, self.view, self.group_fight)
        self.assertEqual(result, True)

    def test_permit_when_post(self):
        self.request.method = 'POST'
        result = self.permission.has_permission(self.request, self.view)
        self.assertEqual(result, True)
