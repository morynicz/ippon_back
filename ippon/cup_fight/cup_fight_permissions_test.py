import datetime
import unittest

import django.test
from django.contrib.auth.models import User

import ippon.models.team_fight as tfm
import ippon.models.team as tem
import ippon.models.tournament as tm
import ippon.cup_fight.permissions as cfp
import ippon.cup_fight.serializers as cfs


class TestCupFightPermissions(django.test.TestCase):
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
        self.permission = cfp.IsCupFightOwnerOrReadOnly()
        self.request = unittest.mock.Mock()
        self.view = unittest.mock.Mock()
        self.request.user = self.admin
        self.cup_phase = self.to.cup_phases.create(name="cp", fight_length=3, final_fight_length=4)
        self.cup_fight = self.cup_phase.cup_fights.create(team_fight=self.tf)
        self.request.data = cfs.CupFightSerializer(self.cup_fight).data


class TestCupFightPermissionNotAdmin(TestCupFightPermissions):
    def setUp(self):
        super(TestCupFightPermissionNotAdmin, self).setUp()

    def test_permits_when_safe_method(self):
        self.request.method = 'GET'
        result = self.permission.has_object_permission(self.request, self.view, self.cup_fight)
        self.assertEqual(result, True)

    def test_doesnt_permit_when_unsafe_method(self):
        self.request.method = 'PUT'
        result = self.permission.has_object_permission(self.request, self.view, self.cup_fight)
        self.assertEqual(result, False)

    def test_doesnt_permit_when_post(self):
        self.request.method = 'POST'
        result = self.permission.has_permission(self.request, self.view)
        self.assertEqual(result, False)


class TestCupFightPermissionAdmin(TestCupFightPermissions):
    def setUp(self):
        super(TestCupFightPermissionAdmin, self).setUp()
        tm.TournamentAdmin.objects.create(user=self.admin, tournament=self.to, is_master=False)

    def test_permits_when_safe_method(self):
        self.request.method = 'GET'
        result = self.permission.has_object_permission(self.request, self.view, self.cup_fight)
        self.assertEqual(result, True)

    def test_permits_when_unsafe_method(self):
        self.request.method = 'PUT'
        result = self.permission.has_object_permission(self.request, self.view, self.cup_fight)
        self.assertEqual(result, True)

    def test_does_permit_when_post(self):
        self.request.method = 'POST'
        result = self.permission.has_permission(self.request, self.view)
        self.assertEqual(result, True)
