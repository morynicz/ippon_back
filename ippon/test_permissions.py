import unittest
import unittest.mock

from ippon import permissions
from ippon.permissions import IsClubAdminOrReadOnlyClub, IsTournamentAdminOrReadOnlyTournament, \
    IsTournamentAdminOrReadOnlyDependent, IsTournamentOwner


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


class TournamentDependentPermissions(unittest.TestCase):
    def setUp(self):
        self.tournament_participation = unittest.mock.Mock()
        self.request = unittest.mock.Mock()
        self.view = unittest.mock.Mock()
        patcher = unittest.mock.patch("ippon.models.TournamentAdmin.objects")
        self.tournament_admin_objects = patcher.start()
        self.addCleanup(patcher.stop)
        self.permission = IsTournamentAdminOrReadOnlyDependent()


class TournamentDependentPermissionsNotAdmin(TournamentDependentPermissions):
    def setUp(self):
        super(TournamentDependentPermissionsNotAdmin, self).setUp()
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
        self.permission = IsTournamentAdminOrReadOnlyDependent()
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
