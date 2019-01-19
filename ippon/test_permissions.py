import datetime
import unittest
import unittest.mock

import django.test
from django.contrib.auth.models import User

import ippon.permissions as permissions
import ippon.serializers as serializers
from ippon.models import Club, Team, Player, TeamFight, TournamentAdmin, Tournament
from ippon.serializers import PointSerializer


class ClubPermissionsTests(django.test.TestCase):
    def setUp(self):
        self.user = User.objects.create(username='user', password='password')
        self.admin = User.objects.create(username='admin', password='password')
        self.club = Club.objects.create(
            name='cn1',
            webpage='http://cw1.co',
            description='cd1',
            city='cc1')
        self.request = unittest.mock.Mock(user=self.user)
        self.view = unittest.mock.Mock()
        self.club_admin = self.club.admins.create(user=self.admin)
        self.permission = permissions.IsClubAdminOrReadOnlyClub()


class ClubPermissionTestsNotAdmin(ClubPermissionsTests):
    def setUp(self):
        super(ClubPermissionTestsNotAdmin, self).setUp()

    def test_permits_when_safe_method(self):
        self.request.method = 'GET'
        result = self.permission.has_object_permission(self.request, self.view, self.club)
        self.assertEqual(result, True)

    def test_doesnt_permit_when_unsafe_method(self):
        self.request.method = 'PUT'
        result = self.permission.has_object_permission(self.request, self.view, self.club)
        self.assertEqual(result, False)


class ClubPermissionTestsAdmin(ClubPermissionsTests):
    def setUp(self):
        super(ClubPermissionTestsAdmin, self).setUp()
        self.club.admins.create(user=self.user)

    def test_doesnt_permit_when_unsafe_method(self):
        self.request.method = 'PUT'
        result = self.permission.has_object_permission(self.request, self.view, self.club)
        self.assertEqual(result, True)


class PlayerPermissionsTest(django.test.TestCase):
    def setUp(self):
        self.user = User.objects.create(username='user', password='password')
        self.admin = User.objects.create(username='admin', password='password')
        self.club = Club.objects.create(
            name='cn1',
            webpage='http://cw1.co',
            description='cd1',
            city='cc1')
        self.player = self.club.players.create(name='pn1', surname='ps1', rank=7,
                                               birthday=datetime.date(year=2001, month=1, day=1), sex=1,
                                               club_id=self.club)
        self.permission = permissions.IsClubAdminOrReadOnlyDependent()
        self.request = unittest.mock.Mock(user=self.user, data=serializers.PlayerSerializer(self.player).data)
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


class TournamentPermissions(django.test.TestCase):
    def setUp(self):
        self.admin = User.objects.create(username='admin', password='password')
        self.user = User.objects.create(username='user', password='password')
        self.tournament = Tournament.objects.create(name='T1', webpage='http://w1.co', description='d1', city='c1',
                                                    date=datetime.date(year=2021, month=1, day=1), address='a1',
                                                    team_size=1, group_match_length=3, ko_match_length=3,
                                                    final_match_length=3, finals_depth=0, age_constraint=5,
                                                    age_constraint_value=20, rank_constraint=5, rank_constraint_value=7,
                                                    sex_constraint=1)
        self.tournament_admin = self.tournament.admins.create(user=self.admin, is_master=True)
        self.request = unittest.mock.Mock(user=self.user)
        self.view = unittest.mock.Mock()
        self.view.kwargs = dict(pk=self.tournament.id)
        self.permission = permissions.IsTournamentAdminOrReadOnlyTournament()


class TournamentPermissionTestsNotAdmin(TournamentPermissions):
    def setUp(self):
        super(TournamentPermissionTestsNotAdmin, self).setUp()

    def test_permits_when_safe_method(self):
        self.request.method = 'GET'
        result = self.permission.has_object_permission(self.request, self.view, self.tournament)
        self.assertEqual(result, True)

    def test_doesnt_permit_when_unsafe_method(self):
        self.request.method = 'PUT'
        result = self.permission.has_object_permission(self.request, self.view, self.tournament)
        self.assertEqual(result, False)


class TournamentPermissionTestsAdmin(TournamentPermissions):
    def setUp(self):
        super(TournamentPermissionTestsAdmin, self).setUp()
        self.tournament_admin = self.tournament.admins.create(user=self.user, is_master=True)

    def test_permits_when_unsafe_method(self):
        self.request.method = 'PUT'
        result = self.permission.has_object_permission(self.request, self.view, self.tournament)
        self.assertEqual(result, True)


class TournamentDependentOrReadOnlyPermissions(django.test.TestCase):
    def setUp(self):
        self.admin = User.objects.create(username='admin', password='password')
        self.to = Tournament.objects.create(name='T1', webpage='http://w1.co', description='d1', city='c1',
                                            date=datetime.date(year=2021, month=1, day=1), address='a1',
                                            team_size=1, group_match_length=3, ko_match_length=3,
                                            final_match_length=3, finals_depth=0, age_constraint=5,
                                            age_constraint_value=20, rank_constraint=5, rank_constraint_value=7,
                                            sex_constraint=1)
        self.tournament_dependent = self.to.group_phases.create(name="a", fight_length=4)
        self.request = unittest.mock.Mock()
        self.permission = permissions.IsTournamentAdminOrReadOnlyDependent()
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
        TournamentAdmin.objects.create(user=self.admin, tournament=self.to, is_master=False)

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
        patcher = unittest.mock.patch("ippon.models.TournamentAdmin.objects")
        self.tournament_admin_objects = patcher.start()
        self.addCleanup(patcher.stop)
        self.permission = permissions.IsTournamentAdminDependent()
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
        self.to = Tournament.objects.create(name='T1', webpage='http://w1.co', description='d1', city='c1',
                                            date=datetime.date(year=2021, month=1, day=1), address='a1',
                                            team_size=1, group_match_length=3, ko_match_length=3,
                                            final_match_length=3, finals_depth=0, age_constraint=5,
                                            age_constraint_value=20, rank_constraint=5, rank_constraint_value=7,
                                            sex_constraint=1)
        self.permission = permissions.IsTournamentOwner()
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


class TestClubOwnerPermissions(django.test.TestCase):
    def setUp(self):
        self.user = User.objects.create(username='user', password='password')
        self.admin = User.objects.create(username='admin', password='password')
        self.club = Club.objects.create(
            name='cn1',
            webpage='http://cw1.co',
            description='cd1',
            city='cc1')
        self.permission = permissions.IsClubOwner()
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


class TestPointPermissions(django.test.TestCase):
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
        self.f = self.tf.fights.create(aka=self.p1, shiro=self.p2)
        self.point = self.f.points.create(player=self.p1, type=0)
        self.permission = permissions.IsPointOwnerOrReadOnly()
        self.request = unittest.mock.Mock()
        self.request.data = PointSerializer(self.point).data
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
        TournamentAdmin.objects.create(user=self.admin, tournament=self.to, is_master=False)

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


class IsTeamOwnerTests(django.test.TestCase):
    def setUp(self):
        self.user = User.objects.create(username='admin', password='password')
        self.to = Tournament.objects.create(name='T1', webpage='http://w1.co', description='d1', city='c1',
                                            date=datetime.date(year=2021, month=1, day=1), address='a1',
                                            team_size=1, group_match_length=3, ko_match_length=3,
                                            final_match_length=3, finals_depth=0, age_constraint=5,
                                            age_constraint_value=20, rank_constraint=5, rank_constraint_value=7,
                                            sex_constraint=1)
        self.team = self.to.teams.create(name="a")
        self.request = unittest.mock.Mock()
        self.view = unittest.mock.Mock()
        self.view.kwargs = dict()
        self.request.user = self.user
        self.permission = permissions.IsTeamOwner()


class IsTeamOwnerAdminTests(IsTeamOwnerTests):
    def setUp(self):
        super(IsTeamOwnerAdminTests, self).setUp()
        TournamentAdmin.objects.create(user=self.user, tournament=self.to, is_master=False)
        self.view.kwargs = dict(pk=self.team.pk)

    def test_does_permit_when_unsafe_method(self):
        self.request.method = 'PUT'
        result = self.permission.has_object_permission(self.request, self.view, self.team)
        self.assertEqual(result, True)

    def test_does_permit_general(self):
        self.request.method = 'PUT'
        result = self.permission.has_permission(self.request, self.view)
        self.assertEqual(result, True)


class IsTeamOwnerNotAdminTests(IsTeamOwnerTests):
    def setUp(self):
        super(IsTeamOwnerNotAdminTests, self).setUp()

    def test_doesnt_permit_when_unsafe_method(self):
        self.request.method = 'PUT'
        result = self.permission.has_object_permission(self.request, self.view, self.team)
        self.assertEqual(result, False)

    def test_doesnt_permit_general(self):
        result = self.permission.has_permission(self.request, self.view)
        self.assertEqual(result, False)
