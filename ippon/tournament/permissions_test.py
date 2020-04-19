import datetime
import json
import unittest

import django.test
from django.contrib.auth.models import User
from rest_framework.test import APIClient

import ippon.tournament.models as tm
import ippon.tournament.permissions as tp
import ippon.club.models as cl


class TournamentPermissionTests(django.test.TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create(username='admin', password='password')
        self.user = User.objects.create(username='user', password='password')
        self.tournament = tm.Tournament.objects.create(name='T1', webpage='http://w1.co', description='d1', city='c1',
                                                       date=datetime.date(year=2021, month=1, day=1), address='a1',
                                                       team_size=1, group_match_length=3, ko_match_length=3,
                                                       final_match_length=3, finals_depth=0, age_constraint=5,
                                                       age_constraint_value=20, rank_constraint=5,
                                                       rank_constraint_value=7,
                                                       sex_constraint=1)
        self.tournament_admin = self.tournament.admins.create(user=self.admin, is_master=True)
        self.request = unittest.mock.Mock(user=self.user)
        self.view = unittest.mock.Mock()
        self.view.kwargs = dict(pk=self.tournament.id)


class TournamentAdminOrReadOnlyPermissions(TournamentPermissionTests):
    def setUp(self):
        super(TournamentAdminOrReadOnlyPermissions, self).setUp()
        self.permission = tp.IsTournamentAdminOrReadOnlyTournament()


class TournamentAdminOrReadOnlyPermissionTestsNotAdmin(TournamentAdminOrReadOnlyPermissions):
    def setUp(self):
        super(TournamentAdminOrReadOnlyPermissionTestsNotAdmin, self).setUp()

    def test_permits_when_safe_method(self):
        self.request.method = 'GET'
        result = self.permission.has_object_permission(self.request, self.view, self.tournament)
        self.assertEqual(result, True)

    def test_doesnt_permit_when_unsafe_method(self):
        self.request.method = 'PUT'
        result = self.permission.has_object_permission(self.request, self.view, self.tournament)
        self.assertEqual(result, False)


class TournamentAdminOrReadOnlyPermissionTestsAdmin(TournamentAdminOrReadOnlyPermissions):
    def setUp(self):
        super(TournamentAdminOrReadOnlyPermissionTestsAdmin, self).setUp()
        self.tournament_admin = self.tournament.admins.create(user=self.user, is_master=True)

    def test_permits_when_unsafe_method(self):
        self.request.method = 'PUT'
        result = self.permission.has_object_permission(self.request, self.view, self.tournament)
        self.assertEqual(result, True)


class TournamentAdminTests(TournamentPermissionTests):
    def setUp(self):
        super(TournamentAdminTests, self).setUp()
        self.permission = tp.IsTournamentAdmin()

    def test_returns_false_when_not_authenticated(self):
        result = self.permission.has_permission(self.request, self.view)
        self.assertEqual(result, False)

    def returns_false_when_not_authorized(self):
        self.client.force_authenticate(user=self.user)
        result = self.permission.has_permission(self.request, self.view)
        self.assertEqual(result, False)

    def test_returns_false_when_view_has_no_pk(self):
        self.view.kwargs = dict()
        result = self.permission.has_permission(self.request, self.view)
        self.assertEqual(result, False)

    def test_returns_true_when_is_tournament_admin(self):
        self.client.force_authenticate(user=self.user)
        self.tournament.admins.create(user=self.user, is_master=False)
        result = self.permission.has_permission(self.request, self.view)
        self.assertEqual(result, True)

    def test_returns_true_when_is_tournament_owner(self):
        self.client.force_authenticate(user=self.user)
        self.tournament.admins.create(user=self.user, is_master=True)
        result = self.permission.has_permission(self.request, self.view)
        self.assertEqual(result, True)


class TournamentDependentOrReadOnlyPermissions(django.test.TestCase):
    def setUp(self):
        self.admin = User.objects.create(username='admin', password='password')
        self.to = tm.Tournament.objects.create(name='T1', webpage='http://w1.co', description='d1', city='c1',
                                               date=datetime.date(year=2021, month=1, day=1), address='a1',
                                               team_size=1, group_match_length=3, ko_match_length=3,
                                               final_match_length=3, finals_depth=0, age_constraint=5,
                                               age_constraint_value=20, rank_constraint=5, rank_constraint_value=7,
                                               sex_constraint=1)
        self.tournament_dependent = self.to.group_phases.create(name="a", fight_length=4)
        self.request = unittest.mock.Mock()
        self.permission = tp.IsTournamentAdminOrReadOnlyDependent()
        self.request.data = {"tournament": self.to.id}
        self.request.user = self.admin
        self.view = unittest.mock.Mock()


class TournamentDependentOrReadOnlyPermissionsNotAdmin(TournamentDependentOrReadOnlyPermissions):
    def setUp(self):
        super(TournamentDependentOrReadOnlyPermissionsNotAdmin, self).setUp()

    def test_permits_when_safe_method(self):
        self.request.method = 'GET'
        result = self.permission.has_object_permission(self.request, self.view, self.tournament_dependent)
        self.assertEqual(result, True)

    def test_doesnt_permit_when_unsafe_method(self):
        self.request.method = 'PUT'
        result = self.permission.has_object_permission(self.request, self.view, self.tournament_dependent)
        self.assertEqual(result, False)

    def test_doesnt_permit_when_post(self):
        self.request.method = 'POST'
        result = self.permission.has_permission(self.request, self.view)
        self.assertEqual(result, False)


class TournamentDependentOrReadOnlyPermissionsAdmin(TournamentDependentOrReadOnlyPermissions):
    def setUp(self):
        super(TournamentDependentOrReadOnlyPermissionsAdmin, self).setUp()
        tm.TournamentAdmin.objects.create(user=self.admin, tournament=self.to, is_master=False)

    def test_permits_when_safe_method(self):
        self.request.method = 'GET'
        result = self.permission.has_object_permission(self.request, self.view, self.tournament_dependent)
        self.assertEqual(result, True)

    def test_permits_when_unsafe_method(self):
        self.request.method = 'PUT'
        result = self.permission.has_object_permission(self.request, self.view, self.tournament_dependent)
        self.assertEqual(result, True)

    def test_does_permit_when_post(self):
        self.request.method = 'POST'
        result = self.permission.has_permission(self.request, self.view)
        self.assertEqual(result, True)


class TournamentDependentPermissions(unittest.TestCase):
    def setUp(self):
        self.tournament_id = 4567
        self.tournament_participation = unittest.mock.Mock()
        self.request = unittest.mock.Mock()
        self.view = unittest.mock.Mock()
        patcher = unittest.mock.patch("ippon.tournament.models.TournamentAdmin.objects")
        self.tournament_admin_objects = patcher.start()
        self.addCleanup(patcher.stop)
        self.permission = tp.IsTournamentAdminDependent()
        self.request.data = {"tournament": self.tournament_id}


class TournamentDependentPermissionsNotAdmin(TournamentDependentPermissions):
    def setUp(self):
        super(TournamentDependentPermissionsNotAdmin, self).setUp()
        self.tournament_admin_objects.all.return_value.filter.return_value = False

    def test_doesnt_permit_when_safe_method(self):
        self.request.method = 'GET'
        result = self.permission.has_object_permission(self.request, self.view, self.tournament_participation)
        self.assertEqual(result, False)
        self.tournament_admin_objects.all.return_value.filter.assert_called_with(user=self.request.user,
                                                                                 tournament=self.tournament_participation.tournament)

    def test_doesnt_permit_when_unsafe_method(self):
        self.request.method = 'PUT'
        result = self.permission.has_object_permission(self.request, self.view, self.tournament_participation)
        self.assertEqual(result, False)
        self.tournament_admin_objects.all.return_value.filter.assert_called_with(user=self.request.user,
                                                                                 tournament=self.tournament_participation.tournament)


class TournamentDependentPermissionsAdmin(TournamentDependentPermissions):
    def setUp(self):
        super(TournamentDependentPermissionsAdmin, self).setUp()
        self.tournament_admin_objects.all.return_value.filter.return_value = True

    def test_permits_when_safe_method(self):
        self.request.method = 'GET'
        result = self.permission.has_object_permission(self.request, self.view, self.tournament_participation)
        self.assertEqual(result, True)

    def test_permits_when_unsafe_method(self):
        self.request.method = 'PUT'
        result = self.permission.has_object_permission(self.request, self.view, self.tournament_participation)
        self.assertEqual(result, True)
        self.tournament_admin_objects.all.return_value.filter.assert_called_with(user=self.request.user,
                                                                                 tournament=self.tournament_participation.tournament)


class TestTournamentOwnerPermissions(django.test.TestCase):
    def setUp(self):
        self.admin = User.objects.create(username='admin', password='password')
        self.user = User.objects.create(username='user', password='password')
        self.to = tm.Tournament.objects.create(name='T1', webpage='http://w1.co', description='d1', city='c1',
                                               date=datetime.date(year=2021, month=1, day=1), address='a1',
                                               team_size=1, group_match_length=3, ko_match_length=3,
                                               final_match_length=3, finals_depth=0, age_constraint=5,
                                               age_constraint_value=20, rank_constraint=5, rank_constraint_value=7,
                                               sex_constraint=1)
        self.permission = tp.IsTournamentOwner()
        self.tournament_admin = self.to.admins.create(user=self.admin, is_master=True)
        self.request = unittest.mock.Mock(user=self.user)
        self.view = unittest.mock.Mock()
        self.view.kwargs = dict(pk=self.to.id)


class TestTournamentOwnerPermissionsAdmin(TestTournamentOwnerPermissions):
    def setUp(self):
        super(TestTournamentOwnerPermissionsAdmin, self).setUp()
        self.to.admins.create(user=self.user, is_master=True)

    def test_permits_object(self):
        result = self.permission.has_object_permission(self.request, self.view, self.tournament_admin)
        self.assertTrue(result)

    def test_permits(self):
        result = self.permission.has_permission(self.request, self.view)
        self.assertTrue(result)


class TestTournamentOwnerPermissionsNotAdmin(TestTournamentOwnerPermissions):
    def setUp(self):
        super(TestTournamentOwnerPermissionsNotAdmin, self).setUp()

    def test_does_not_permit_object(self):
        result = self.permission.has_object_permission(self.request, self.view, self.tournament_admin)
        self.assertFalse(result)

    def test_does_not_permit(self):
        result = self.permission.has_permission(self.request, self.view)
        self.assertFalse(result)


class TestTournamentOwnerAdminCreationPermissions(django.test.TestCase):
    def setUp(self):
        self.user = User.objects.create(username='user', password='password')
        self.admin = User.objects.create(username='admin', password='password')
        self.new_admin = User.objects.create(username='newguy', password='password')
        self.tournament = tm.Tournament.objects.create(
            name='T1', webpage='http://w1.co', description='d1', city='c1',
            date=datetime.date(year=2021, month=1, day=1), address='a1',
            team_size=1, group_match_length=3, ko_match_length=3,
            final_match_length=3, finals_depth=0, age_constraint=5,
            age_constraint_value=20, rank_constraint=5, rank_constraint_value=7,
            sex_constraint=1)
        self.permission = tp.IsTournamentOwnerAdminCreation()
        self.request = unittest.mock.Mock(user=self.user)
        self.request.body = json.dumps({
            "id": -1,
            "tournament_id": self.tournament.id,
            "user": {
                "id": self.new_admin.id,
                "username": self.new_admin.username
            },
            "is_master": False
        })
        self.view = unittest.mock.Mock()
        self.view.kwargs = dict()
        self.tournament_admin = self.tournament.admins.create(user=self.admin, is_master=True)


class TestTournamentOwnerAdminCreationPermissionsOwner(TestTournamentOwnerAdminCreationPermissions):
    def setUp(self):
        super(TestTournamentOwnerAdminCreationPermissionsOwner, self).setUp()
        self.tournament.admins.create(user=self.user, is_master=True)

    def test_permits_when_is_owner_for_object(self):
        result = self.permission.has_object_permission(self.request, self.view, self.tournament_admin)
        self.assertTrue(result)

    def test_permits_when_is_owner(self):
        result = self.permission.has_permission(self.request, self.view)
        self.assertTrue(result)


class TestTournamentOwnerAdminCreationPermissionsAdmin(TestTournamentOwnerAdminCreationPermissions):
    def setUp(self):
        super(TestTournamentOwnerAdminCreationPermissionsAdmin, self).setUp()
        self.tournament.admins.create(user=self.user, is_master=False)

    def test_does_not_permit_when_is_not_owner_for_object(self):
        result = self.permission.has_object_permission(self.request, self.view, self.tournament_admin)
        self.assertFalse(result)

    def test_does_not_permit_when_is_not_owner(self):
        result = self.permission.has_permission(self.request, self.view)
        self.assertFalse(result)


class TestTournamentOwnerAdminCreationPermissionsNotAdmin(TestTournamentOwnerAdminCreationPermissions):
    def setUp(self):
        super(TestTournamentOwnerAdminCreationPermissionsNotAdmin, self).setUp()

    def test_does_not_permit_when_is_not_owner_for_object(self):
        result = self.permission.has_object_permission(self.request, self.view, self.tournament_admin)
        self.assertFalse(result)

    def test_does_not_permit_when_is_not_owner(self):
        result = self.permission.has_permission(self.request, self.view)
        self.assertFalse(result)


class TestTournamentOwnerParticipantCreationPermissions(django.test.TestCase):
    def setUp(self):
        self.user = User.objects.create(username='user', password='password')
        self.admin = User.objects.create(username='admin', password='password')
        self.new_admin = User.objects.create(username='newguy', password='password')
        self.tournament = tm.Tournament.objects.create(
            name='T1', webpage='http://w1.co', description='d1', city='c1',
            date=datetime.date(year=2021, month=1, day=1), address='a1',
            team_size=1, group_match_length=3, ko_match_length=3,
            final_match_length=3, finals_depth=0, age_constraint=5,
            age_constraint_value=20, rank_constraint=5, rank_constraint_value=7,
            sex_constraint=1)
        self.club = cl.Club.objects.create(
            name='cn1',
            webpage='http://cw1.co',
            description='cd1',
            city='cc1')
        self.player = self.club.players.create(name='pn1', surname='ps1', rank=7,
                                               birthday=datetime.date(year=2001, month=1, day=1), sex=1,
                                               club_id=self.club)
        self.permission = tp.IsTournamentAdminParticipantCreation()
        self.request = unittest.mock.Mock(user=self.user)
        self.request.body = json.dumps({
            "player": {"id": self.player.id,
                       "name": self.player.name,
                       "surname": self.player.surname
                       },
            "tournament_id": self.tournament.id,
            "is_paid": False,
            "is_registered": False,
            "is_qualified": False,
            "is_sex_ok": False,
            "is_rank_ok": False,
            "is_age_ok": False,
            "id": 0,
            "notes": ""
        })
        self.view = unittest.mock.Mock()
        self.view.kwargs = dict()
        self.tournament_admin = self.tournament.admins.create(user=self.admin, is_master=True)


class TestTournamentOwnerParticipantCreationPermissionsOwner(TestTournamentOwnerParticipantCreationPermissions):
    def setUp(self):
        super(TestTournamentOwnerParticipantCreationPermissionsOwner, self).setUp()
        self.tournament.admins.create(user=self.user, is_master=True)

    def test_permits_when_is_owner_for_object(self):
        result = self.permission.has_object_permission(self.request, self.view, self.tournament_admin)
        self.assertTrue(result)

    def test_permits_when_is_owner(self):
        result = self.permission.has_permission(self.request, self.view)
        self.assertTrue(result)


class TestTournamentOwnerParticipantCreationPermissionsAdmin(TestTournamentOwnerParticipantCreationPermissions):
    def setUp(self):
        super(TestTournamentOwnerParticipantCreationPermissionsAdmin, self).setUp()
        self.tournament.admins.create(user=self.user, is_master=False)

    def test_permits_when_is_admin_for_object(self):
        result = self.permission.has_object_permission(self.request, self.view, self.tournament_admin)
        self.assertTrue(result)

    def test_permits_when_is_admin(self):
        result = self.permission.has_permission(self.request, self.view)
        self.assertTrue(result)


class TestTournamentOwnerParticipantCreationPermissionsNotAdmin(TestTournamentOwnerParticipantCreationPermissions):
    def setUp(self):
        super(TestTournamentOwnerParticipantCreationPermissionsNotAdmin, self).setUp()

    def test_does_not_permit_when_is_not_admin_for_object(self):
        result = self.permission.has_object_permission(self.request, self.view, self.tournament_admin)
        self.assertFalse(result)

    def test_does_not_permit_when_is_not_admin(self):
        result = self.permission.has_permission(self.request, self.view)
        self.assertFalse(result)
