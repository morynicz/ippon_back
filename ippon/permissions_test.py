import datetime
import json
import unittest
import unittest.mock

import django.test
from django.contrib.auth.models import User

import ippon.club.permissisons as clp
import ippon.point.permissions as ptp
import ippon.team_fight.models as tfm
import ippon.team.models as tem
import ippon.tournament.models as tm
import ippon.player.models as plm
import ippon.club.models as cl
import ippon.point.serializers as pts


class TestClubOwnerPermissions(django.test.TestCase):
    def setUp(self):
        self.user = User.objects.create(username='user', password='password')
        self.admin = User.objects.create(username='admin', password='password')
        self.club = cl.Club.objects.create(
            name='cn1',
            webpage='http://cw1.co',
            description='cd1',
            city='cc1')
        self.permission = clp.IsClubOwner()
        self.request = unittest.mock.Mock(user=self.user)
        self.view = unittest.mock.Mock()
        self.view.kwargs = dict(pk=self.club.id)
        self.club_admin = self.club.admins.create(user=self.admin)


class TestClubOwnerPermissionsAdmin(TestClubOwnerPermissions):
    def setUp(self):
        super(TestClubOwnerPermissionsAdmin, self).setUp()
        self.club.admins.create(user=self.user)

    def test_permits_when_is_owner_for_object(self):
        result = self.permission.has_object_permission(self.request, self.view, self.club_admin)
        self.assertTrue(result)

    def test_permits_when_is_owner(self):
        result = self.permission.has_permission(self.request, self.view)
        self.assertTrue(result)


class TestClubOwnerPermissionsNotAdmin(TestClubOwnerPermissions):
    def setUp(self):
        super(TestClubOwnerPermissionsNotAdmin, self).setUp()

    def test_does_not_permit_when_is_not_owner_for_object(self):
        result = self.permission.has_object_permission(self.request, self.view, self.club_admin)
        self.assertFalse(result)

    def test_does_not_permit_when_is_not_owner(self):
        result = self.permission.has_permission(self.request, self.view)
        self.assertFalse(result)


class TestClubOwnerAdminCreationPermissions(django.test.TestCase):
    def setUp(self):
        self.user = User.objects.create(username='user', password='password')
        self.admin = User.objects.create(username='admin', password='password')
        self.new_admin = User.objects.create(username='newguy', password='password')
        self.club = cl.Club.objects.create(
            name='cn1',
            webpage='http://cw1.co',
            description='cd1',
            city='cc1')
        self.permission = clp.IsClubOwnerAdminCreation()
        self.request = unittest.mock.Mock(user=self.user)
        self.request.body = json.dumps({
            "id": -1,
            "club_id": self.club.id,
            "user": {
                "id": self.new_admin.id,
                "username": self.new_admin.username
            }
        })
        self.view = unittest.mock.Mock()
        self.view.kwargs = dict()
        self.club_admin = self.club.admins.create(user=self.admin)


class TestClubOwnerAdminCreationPermissionsAdmin(TestClubOwnerAdminCreationPermissions):
    def setUp(self):
        super(TestClubOwnerAdminCreationPermissionsAdmin, self).setUp()
        self.club.admins.create(user=self.user)

    def test_permits_when_is_owner_for_object(self):
        result = self.permission.has_object_permission(self.request, self.view, self.club_admin)
        self.assertTrue(result)

    def test_permits_when_is_owner(self):
        result = self.permission.has_permission(self.request, self.view)
        self.assertTrue(result)


class TestClubOwnerAdminCreationPermissionsNotAdmin(TestClubOwnerAdminCreationPermissions):
    def setUp(self):
        super(TestClubOwnerAdminCreationPermissionsNotAdmin, self).setUp()

    def test_does_not_permit_when_is_not_owner_for_object(self):
        result = self.permission.has_object_permission(self.request, self.view, self.club_admin)
        self.assertFalse(result)

    def test_does_not_permit_when_is_not_owner(self):
        result = self.permission.has_permission(self.request, self.view)
        self.assertFalse(result)


class TestPointPermissions(django.test.TestCase):
    def setUp(self):
        c = cl.Club.objects.create(
            name='cn1',
            webpage='http://cw1.co',
            description='cd1',
            city='cc1')
        self.admin = User.objects.create(username='admin', password='password')
        self.to = tm.Tournament.objects.create(name='T1', webpage='http://w1.co', description='d1', city='c1',
                                               date=datetime.date(year=2021, month=1, day=1), address='a1',
                                               team_size=1, group_match_length=3, ko_match_length=3,
                                               final_match_length=3, finals_depth=0, age_constraint=5,
                                               age_constraint_value=20, rank_constraint=5, rank_constraint_value=7,
                                               sex_constraint=1)
        self.t1 = tem.Team.objects.create(tournament=self.to, name='t1')
        self.p1 = plm.Player.objects.create(name='pn1', surname='ps1', rank=7,
                                            birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=c)
        self.t1.team_members.create(player=self.p1)
        self.t2 = tem.Team.objects.create(tournament=self.to, name='t2')
        self.p2 = plm.Player.objects.create(name='pn2', surname='ps2', rank=7,
                                            birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=c)
        self.t2.team_members.create(player=self.p2)

        self.tf = tfm.TeamFight.objects.create(aka_team=self.t1, shiro_team=self.t2, tournament=self.to)
        self.f = self.tf.fights.create(aka=self.p1, shiro=self.p2)
        self.point = self.f.points.create(player=self.p1, type=0)
        self.permission = ptp.IsPointOwnerOrReadOnly()
        self.request = unittest.mock.Mock()
        self.request.data = pts.PointSerializer(self.point).data
        self.view = unittest.mock.Mock()
        self.view.kwargs = dict()
        self.request.user = self.admin


class TestPointPermissionNotAdmin(TestPointPermissions):
    def setUp(self):
        super(TestPointPermissionNotAdmin, self).setUp()

    def test_permits_when_safe_method(self):
        self.request.method = 'GET'
        result = self.permission.has_object_permission(self.request, self.view, self.point)
        self.assertEqual(result, True)

    def test_doesnt_permit_when_unsafe_method(self):
        self.request.method = 'PUT'
        result = self.permission.has_object_permission(self.request, self.view, self.point)
        self.assertEqual(result, False)

    def test_doesnt_permit_general(self):
        self.request.method = 'POST'
        result = self.permission.has_permission(self.request, self.view)
        self.assertEqual(result, False)


class TestPointPermissionAdmin(TestPointPermissions):
    def setUp(self):
        super(TestPointPermissionAdmin, self).setUp()
        tm.TournamentAdmin.objects.create(user=self.admin, tournament=self.to, is_master=False)

    def test_permits_when_safe_method(self):
        self.request.method = 'GET'
        result = self.permission.has_object_permission(self.request, self.view, self.point)
        self.assertEqual(result, True)

    def test_does_permit_when_unsafe_method(self):
        self.request.method = 'PUT'
        result = self.permission.has_object_permission(self.request, self.view, self.point)
        self.assertEqual(result, True)

    def test_permits_general(self):
        self.request.method = 'PUT'
        result = self.permission.has_permission(self.request, self.view)
        self.assertEqual(result, True)
