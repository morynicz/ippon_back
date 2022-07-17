import django.test
import json
import unittest
from django.contrib.auth.models import User

import ippon.club.permissisons as clp
import ippon.models.club as cl


class ClubPermissionsTests(django.test.TestCase):
    def setUp(self):
        self.user = User.objects.create(username="user", password="password")
        self.admin = User.objects.create(username="admin", password="password")
        self.club = cl.Club.objects.create(name="cn1", webpage="http://cw1.co", description="cd1", city="cc1")
        self.request = unittest.mock.Mock(user=self.user)
        self.view = unittest.mock.Mock()
        self.club_admin = self.club.admins.create(user=self.admin)
        self.permission = clp.IsClubAdminOrReadOnlyClub()


class ClubPermissionTestsNotAdmin(ClubPermissionsTests):
    def setUp(self):
        super(ClubPermissionTestsNotAdmin, self).setUp()

    def test_permits_when_safe_method(self):
        self.request.method = "GET"
        result = self.permission.has_object_permission(self.request, self.view, self.club)
        self.assertEqual(result, True)

    def test_doesnt_permit_when_unsafe_method(self):
        self.request.method = "PUT"
        result = self.permission.has_object_permission(self.request, self.view, self.club)
        self.assertEqual(result, False)


class ClubPermissionTestsAdmin(ClubPermissionsTests):
    def setUp(self):
        super(ClubPermissionTestsAdmin, self).setUp()
        self.club.admins.create(user=self.user)

    def test_doesnt_permit_when_unsafe_method(self):
        self.request.method = "PUT"
        result = self.permission.has_object_permission(self.request, self.view, self.club)
        self.assertEqual(result, True)


class TestClubOwnerPermissions(django.test.TestCase):
    def setUp(self):
        self.user = User.objects.create(username="user", password="password")
        self.admin = User.objects.create(username="admin", password="password")
        self.club = cl.Club.objects.create(name="cn1", webpage="http://cw1.co", description="cd1", city="cc1")
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
        self.user = User.objects.create(username="user", password="password")
        self.admin = User.objects.create(username="admin", password="password")
        self.new_admin = User.objects.create(username="newguy", password="password")
        self.club = cl.Club.objects.create(name="cn1", webpage="http://cw1.co", description="cd1", city="cc1")
        self.permission = clp.IsClubOwnerAdminCreation()
        self.request = unittest.mock.Mock(user=self.user)
        self.request.body = json.dumps(
            {
                "id": -1,
                "club_id": self.club.id,
                "user": {"id": self.new_admin.id, "username": self.new_admin.username},
            }
        )
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
