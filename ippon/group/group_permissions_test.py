import datetime
import django.test
import unittest
from django.contrib.auth.models import User

import ippon.group.permissions as gp
import ippon.group.serializers as gs
import ippon.models.tournament as tm


class TestGroupPermissions(django.test.TestCase):
    def setUp(self):
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
        self.group_phase = self.to.group_phases.create(fight_length=3)
        self.group = self.group_phase.groups.create(name="G1")
        self.request = unittest.mock.Mock()
        self.view = unittest.mock.Mock()
        self.view.kwargs = dict()
        self.request.user = self.admin
        self.request.data = gs.GroupSerializer(self.group).data


class TestGroupOwnerOrReadOnlyPermissions(TestGroupPermissions):
    def setUp(self):
        super(TestGroupOwnerOrReadOnlyPermissions, self).setUp()
        self.permission = gp.IsGroupOwnerOrReadOnly()


class TestGroupOwnerOrReadOnlyPermissionNotAdmin(TestGroupOwnerOrReadOnlyPermissions):
    def setUp(self):
        super(TestGroupOwnerOrReadOnlyPermissionNotAdmin, self).setUp()

    def test_permits_when_safe_method(self):
        self.request.method = "GET"
        result = self.permission.has_object_permission(
            self.request, self.view, self.group
        )
        self.assertEqual(result, True)

    def test_doesnt_permit_when_unsafe_method(self):
        self.request.method = "PUT"
        result = self.permission.has_object_permission(
            self.request, self.view, self.group
        )
        self.assertEqual(result, False)

    def test_doesnt_permit_when_post(self):
        self.request.method = "POST"
        result = self.permission.has_permission(self.request, self.view)
        self.assertEqual(result, False)


class TestGroupOwnerOrReadOnlyPermissionAdmin(TestGroupOwnerOrReadOnlyPermissions):
    def setUp(self):
        super(TestGroupOwnerOrReadOnlyPermissionAdmin, self).setUp()
        tm.TournamentAdmin.objects.create(
            user=self.admin, tournament=self.to, is_master=False
        )

    def test_permits_when_safe_method(self):
        self.request.method = "GET"
        result = self.permission.has_object_permission(
            self.request, self.view, self.group
        )
        self.assertEqual(result, True)

    def test_does_permit_when_unsafe_method(self):
        self.request.method = "PUT"
        result = self.permission.has_object_permission(
            self.request, self.view, self.group
        )
        self.assertEqual(result, True)

    def test_does_permit_when_post(self):
        self.request.method = "POST"
        result = self.permission.has_permission(self.request, self.view)
        self.assertEqual(result, True)


class TestGroupOwnerPermissions(TestGroupPermissions):
    def setUp(self):
        super(TestGroupOwnerPermissions, self).setUp()
        self.permission = gp.IsGroupOwner()


class TestGroupOwnerPermissionNotAdmin(TestGroupOwnerPermissions):
    def setUp(self):
        super(TestGroupOwnerPermissionNotAdmin, self).setUp()

    def test_doesnt_permit_when_unsafe_method(self):
        self.request.method = "PUT"
        result = self.permission.has_object_permission(
            self.request, self.view, self.group
        )
        self.assertEqual(result, False)

    def test_doesnt_permit_general(self):
        result = self.permission.has_permission(self.request, self.view)
        self.assertEqual(result, False)


class TestGroupOwnerPermissionAdmin(TestGroupOwnerPermissions):
    def setUp(self):
        super(TestGroupOwnerPermissionAdmin, self).setUp()
        tm.TournamentAdmin.objects.create(
            user=self.admin, tournament=self.to, is_master=False
        )
        self.view.kwargs = dict(pk=self.group.pk)

    def test_does_permit_when_unsafe_method(self):
        self.request.method = "PUT"
        result = self.permission.has_object_permission(
            self.request, self.view, self.group
        )
        self.assertEqual(result, True)

    def test_does_permit_general(self):
        self.request.method = "PUT"
        result = self.permission.has_permission(self.request, self.view)
        self.assertEqual(result, True)
