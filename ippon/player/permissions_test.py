import datetime
import unittest

import django.test
from django.contrib.auth.models import User

import ippon.club.models as clm
import ippon.club.permissisons as clp
import ippon.player.serializers as pls


class PlayerPermissionsTest(django.test.TestCase):
    def setUp(self):
        self.user = User.objects.create(username='user', password='password')
        self.admin = User.objects.create(username='admin', password='password')
        self.club = clm.Club.objects.create(
            name='cn1',
            webpage='http://cw1.co',
            description='cd1',
            city='cc1')
        self.player = self.club.players.create(name='pn1', surname='ps1', rank=7,
                                               birthday=datetime.date(year=2001, month=1, day=1), sex=1,
                                               club_id=self.club)
        self.permission = clp.IsClubAdminOrReadOnlyDependent()
        self.request = unittest.mock.Mock(user=self.user, data=pls.PlayerSerializer(self.player).data)
        self.view = unittest.mock.Mock()
        self.club_admin = self.club.admins.create(user=self.admin)


class PlayerPermissionTestsNotAdmin(PlayerPermissionsTest):
    def setUp(self):
        super(PlayerPermissionTestsNotAdmin, self).setUp()

    def test_permits_when_safe_method(self):
        self.request.method = 'GET'
        result = self.permission.has_object_permission(self.request, self.view, self.player)
        self.assertEqual(result, True)

    def test_doesnt_permit_when_unsafe_method(self):
        self.request.method = 'PUT'
        result = self.permission.has_object_permission(self.request, self.view, self.player)
        self.assertEqual(result, False)

    def test_doesnt_permit_when_post(self):
        self.request.method = 'POST'
        result = self.permission.has_permission(self.request, self.view)
        self.assertEqual(result, False)


class PlayerPermissionTestsAdmin(PlayerPermissionsTest):
    def setUp(self):
        super(PlayerPermissionTestsAdmin, self).setUp()
        self.club.admins.create(user=self.user)

    def test_permits_when_safe_method(self):
        self.request.method = 'GET'
        result = self.permission.has_object_permission(self.request, self.view, self.player)
        self.assertEqual(result, True)

    def test_permits_when_unsafe_method(self):
        self.request.method = 'PUT'
        result = self.permission.has_object_permission(self.request, self.view, self.player)
        self.assertEqual(result, True)
