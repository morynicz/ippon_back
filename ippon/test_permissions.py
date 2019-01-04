import datetime
import unittest
import unittest.mock

import django.test
from django.contrib.auth.models import User

from ippon import permissions
from ippon.models import Club, Team, Player, TeamFight, TournamentAdmin, Tournament
from ippon.permissions import IsClubAdminOrReadOnlyClub, IsTournamentAdminOrReadOnlyTournament, \
    IsTournamentAdminOrReadOnlyDependent, IsTournamentOwner, IsClubOwner, IsPointOwnerOrReadOnly, \
    IsTournamentAdminDependent, IsGroupOwnerOrReadOnly


class ClubPermissionsTests(unittest.TestCase):
    def setUp(self):
        self.club = unittest.mock.Mock()
        self.request = unittest.mock.Mock()
        self.view = unittest.mock.Mock()
        patcher = unittest.mock.patch("ippon.models.ClubAdmin.objects")
        self.club_admin_objects = patcher.start()
        self.addCleanup(patcher.stop)
        self.permission = IsClubAdminOrReadOnlyClub()


class ClubPermissionTestsNotAdmin(ClubPermissionsTests):
    def setUp(self):
        super(ClubPermissionTestsNotAdmin, self).setUp()
        self.club_admin_objects.all.return_value.filter.return_value = False

    def test_permits_when_safe_method(self):
        self.request.method = 'GET'
        result = self.permission.has_object_permission(self.request, self.view, self.club)
        self.assertEqual(result, True)

    def test_doesnt_permit_when_unsafe_method(self):
        self.request.method = 'PUT'
        result = self.permission.has_object_permission(self.request, self.view, self.club)
        self.assertEqual(result, False)
        self.club_admin_objects.all.return_value.filter.assert_called_with(user=self.request.user, club=self.club)


class ClubPermissionTestsAdmin(ClubPermissionsTests):
    def setUp(self):
        super(ClubPermissionTestsAdmin, self).setUp()
        self.club_admin_objects.all.return_value.filter.return_value = True

    def test_doesnt_permit_when_unsafe_method(self):
        self.request.method = 'PUT'
        result = self.permission.has_object_permission(self.request, self.view, self.club)
        self.assertEqual(result, True)
        self.club_admin_objects.all.return_value.filter.assert_called_with(user=self.request.user, club=self.club)


class PlayerPermissionsTest(unittest.TestCase):
    def setUp(self):
        self.player = unittest.mock.Mock()
        self.request = unittest.mock.Mock()
        self.view = unittest.mock.Mock()
        patcher = unittest.mock.patch("ippon.models.ClubAdmin.objects")
        self.club_admin_objects = patcher.start()
        self.addCleanup(patcher.stop)
        self.permission = permissions.IsClubAdminOrReadOnlyDependent()


class PlayerPermissionTestsNotAdmin(PlayerPermissionsTest):
    def setUp(self):
        super(PlayerPermissionTestsNotAdmin, self).setUp()
        self.club_admin_objects.all.return_value.filter.return_value = False

    def test_permits_when_safe_method(self):
        self.request.method = 'GET'
        result = self.permission.has_object_permission(self.request, self.view, self.player)
        self.assertEqual(result, True)

    def test_doesnt_permit_when_unsafe_method(self):
        self.request.method = 'PUT'
        result = self.permission.has_object_permission(self.request, self.view, self.player)
        self.assertEqual(result, False)
        self.club_admin_objects.all.return_value.filter.assert_called_with(user=self.request.user,
                                                                           club=self.player.club_id)


class PlayerPermissionTestsAdmin(PlayerPermissionsTest):
    def setUp(self):
        super(PlayerPermissionTestsAdmin, self).setUp()
        self.club_admin_objects.all.return_value.filter.return_value = True

    def test_permits_when_safe_method(self):
        self.request.method = 'GET'
        result = self.permission.has_object_permission(self.request, self.view, self.player)
        self.assertEqual(result, True)

    def test_permits_when_unsafe_method(self):
        self.request.method = 'PUT'
        result = self.permission.has_object_permission(self.request, self.view, self.player)
        self.assertEqual(result, True)
        self.club_admin_objects.all.return_value.filter.assert_called_with(user=self.request.user,
                                                                           club=self.player.club_id)


class TournamentPermissions(unittest.TestCase):
    def setUp(self):
        self.tournament = unittest.mock.Mock()
        self.request = unittest.mock.Mock()
        self.view = unittest.mock.Mock()
        patcher = unittest.mock.patch("ippon.models.TournamentAdmin.objects")
        self.tournament_admin_objects = patcher.start()
        self.addCleanup(patcher.stop)
        self.permission = IsTournamentAdminOrReadOnlyTournament()


class TournamentPermissionTestsNotAdmin(TournamentPermissions):
    def setUp(self):
        super(TournamentPermissionTestsNotAdmin, self).setUp()
        self.tournament_admin_objects.all.return_value.filter.return_value = False

    def test_permits_when_safe_method(self):
        self.request.method = 'GET'
        result = self.permission.has_object_permission(self.request, self.view, self.tournament)
        self.assertEqual(result, True)

    def test_doesnt_permit_when_unsafe_method(self):
        self.request.method = 'PUT'
        result = self.permission.has_object_permission(self.request, self.view, self.tournament)
        self.assertEqual(result, False)
        self.tournament_admin_objects.all.return_value.filter.assert_called_with(user=self.request.user,
                                                                                 tournament=self.tournament)


class TournamentPermissionTestsAdmin(TournamentPermissions):
    def setUp(self):
        super(TournamentPermissionTestsAdmin, self).setUp()
        self.tournament_admin_objects.all.return_value.filter.return_value = True

    def test_doesnt_permit_when_unsafe_method(self):
        self.request.method = 'PUT'
        result = self.permission.has_object_permission(self.request, self.view, self.tournament)
        self.assertEqual(result, True)
        self.tournament_admin_objects.all.return_value.filter.assert_called_with(user=self.request.user,
                                                                                 tournament=self.tournament)


class TournamentDependentOrReadOnlyPermissions(unittest.TestCase):
    def setUp(self):
        self.tournament_participation = unittest.mock.Mock()
        self.request = unittest.mock.Mock()
        self.view = unittest.mock.Mock()
        patcher = unittest.mock.patch("ippon.models.TournamentAdmin.objects")
        self.tournament_admin_objects = patcher.start()
        self.addCleanup(patcher.stop)
        self.permission = IsTournamentAdminOrReadOnlyDependent()


class TournamentDependentOrReadOnlyPermissionsNotAdmin(TournamentDependentOrReadOnlyPermissions):
    def setUp(self):
        super(TournamentDependentOrReadOnlyPermissionsNotAdmin, self).setUp()
        self.tournament_admin_objects.all.return_value.filter.return_value = False

    def test_permits_when_safe_method(self):
        self.request.method = 'GET'
        result = self.permission.has_object_permission(self.request, self.view, self.tournament_participation)
        self.assertEqual(result, True)

    def test_doesnt_permit_when_unsafe_method(self):
        self.request.method = 'PUT'
        result = self.permission.has_object_permission(self.request, self.view, self.tournament_participation)
        self.assertEqual(result, False)
        self.tournament_admin_objects.all.return_value.filter.assert_called_with(user=self.request.user,
                                                                                 tournament=self.tournament_participation.tournament)


class TournamentDependentOrReadOnlyPermissionsAdmin(TournamentDependentOrReadOnlyPermissions):
    def setUp(self):
        super(TournamentDependentOrReadOnlyPermissionsAdmin, self).setUp()
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


class TournamentDependentPermissions(unittest.TestCase):
    def setUp(self):
        self.tournament_participation = unittest.mock.Mock()
        self.request = unittest.mock.Mock()
        self.view = unittest.mock.Mock()
        patcher = unittest.mock.patch("ippon.models.TournamentAdmin.objects")
        self.tournament_admin_objects = patcher.start()
        self.addCleanup(patcher.stop)
        self.permission = IsTournamentAdminDependent()


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


class TestTournamentOwnerPermissions(unittest.TestCase):
    def setUp(self):
        patcher = unittest.mock.patch("ippon.models.TournamentAdmin.objects")
        self.tournament_admin_objects = patcher.start()
        self.addCleanup(patcher.stop)
        self.permission = IsTournamentOwner()
        self.tournament_admin = unittest.mock.Mock()
        self.request = unittest.mock.Mock()
        self.view = unittest.mock.Mock()

    def test_does_not_permit_when_is_not_owner(self):
        self.owner_permission_test(False)

    def test_permits_when_is_owner(self):
        self.owner_permission_test(True)

    def owner_permission_test(self, is_owner):
        self.tournament_admin_objects.filter.return_value = is_owner
        result = self.permission.has_object_permission(self.request, self.view, self.tournament_admin)
        self.assertEqual(result, is_owner)
        self.tournament_admin_objects.filter.assert_called_with(user=self.request.user,
                                                                tournament=self.tournament_admin.tournament,
                                                                is_master=True)


class TestClubOwnerPermissions(unittest.TestCase):
    def setUp(self):
        patcher = unittest.mock.patch("ippon.models.ClubAdmin.objects")
        self.club_admin_objects = patcher.start()
        self.addCleanup(patcher.stop)
        self.permission = IsClubOwner()
        self.club_admin = unittest.mock.Mock()
        self.request = unittest.mock.Mock()
        self.view = unittest.mock.Mock()

    def test_does_not_permit_when_is_not_owner(self):
        self.owner_permission_test(False)

    def test_permits_when_is_owner(self):
        self.owner_permission_test(True)

    def owner_permission_test(self, is_owner):
        self.club_admin_objects.filter.return_value = is_owner
        result = self.permission.has_object_permission(self.request, self.view, self.club_admin)
        self.assertEqual(result, is_owner)
        self.club_admin_objects.filter.assert_called_with(user=self.request.user,
                                                          club=self.club_admin.club)


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
        self.permission = IsPointOwnerOrReadOnly()
        self.request = unittest.mock.Mock()
        self.view = unittest.mock.Mock()
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


class TestGroupPermissions(django.test.TestCase):
    def setUp(self):
        self.admin = User.objects.create(username='admin', password='password')
        self.to = Tournament.objects.create(name='T1', webpage='http://w1.co', description='d1', city='c1',
                                            date=datetime.date(year=2021, month=1, day=1), address='a1',
                                            team_size=1, group_match_length=3, ko_match_length=3,
                                            final_match_length=3, finals_depth=0, age_constraint=5,
                                            age_constraint_value=20, rank_constraint=5, rank_constraint_value=7,
                                            sex_constraint=1)
        self.group_phase = self.to.group_phases.create(fight_length=3)
        self.group = self.group_phase.groups.create(name='G1')
        self.permission = IsGroupOwnerOrReadOnly()
        self.request = unittest.mock.Mock()
        self.view = unittest.mock.Mock()
        self.request.user = self.admin


class TestGroupPermissionNotAdmin(TestGroupPermissions):
    def setUp(self):
        super(TestGroupPermissionNotAdmin, self).setUp()

    def test_permits_when_safe_method(self):
        self.request.method = 'GET'
        result = self.permission.has_object_permission(self.request, self.view, self.group)
        self.assertEqual(result, True)

    def test_doesnt_permit_when_unsafe_method(self):
        self.request.method = 'PUT'
        result = self.permission.has_object_permission(self.request, self.view, self.group)
        self.assertEqual(result, False)


class TestGroupPermissionAdmin(TestGroupPermissions):
    def setUp(self):
        super(TestGroupPermissionAdmin, self).setUp()
        TournamentAdmin.objects.create(user=self.admin, tournament=self.to, is_master=False)

    def test_permits_when_safe_method(self):
        self.request.method = 'GET'
        result = self.permission.has_object_permission(self.request, self.view, self.group)
        self.assertEqual(result, True)

    def test_does_permit_when_unsafe_method(self):
        self.request.method = 'PUT'
        result = self.permission.has_object_permission(self.request, self.view, self.group)
        self.assertEqual(result, True)
