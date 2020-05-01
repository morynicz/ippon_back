from django.urls.base import reverse
from rest_framework import status

import ippon.models.group_phase as gpm
import ippon.models.tournament as tm
import ippon.utils.authorization_test_fixtures as iua


class TournamentGroupAuthorizationAuthenticatedTests(iua.AuthorizationViewsAuthenticatedTests):
    def setUp(self):
        super(TournamentGroupAuthorizationAuthenticatedTests, self).setUp()
        self.group_phase = gpm.GroupPhase.objects.create(name="gp1", tournament=self.tournament, fight_length=3)

    def test_tournament_group_authorization_returns_negative_auth_if_not_authorized(self):
        g1 = self.group_phase.groups.create(name="g1")
        expected = {
            "isAuthorized": False
        }

        response = self.client.get(reverse('group-authorization', kwargs={'pk': g1.pk}))
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_tournament_group_authorization_returns_positive_auth_if_authorized_staff(self):
        self.parametrized_group_authorization_returns_positive_auth_if_authorized(False)

    def test_tournament_group_authorization_returns_positive_auth_if_authorized_admin(self):
        self.parametrized_group_authorization_returns_positive_auth_if_authorized(True)

    def parametrized_group_authorization_returns_positive_auth_if_authorized(self, is_admin):
        tm.TournamentAdmin.objects.create(user=self.u1, tournament=self.tournament, is_master=is_admin)
        g1 = self.group_phase.groups.create(name="g1")
        expected = {
            "isAuthorized": True
        }
        response = self.client.get(reverse('group-authorization', kwargs={'pk': g1.pk}))
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class GroupViewsUnauthenticatedTests(iua.AuthorizationViewsUnauthenticatedTests):
    def setUp(self):
        super(GroupViewsUnauthenticatedTests, self).setUp()

    def test_tournament_group_authorization_returns_negative_auth(self):
        group_phase = gpm.GroupPhase.objects.create(name="gp1", tournament=self.tournament, fight_length=3)
        g1 = group_phase.groups.create(name="g1")
        expected = {
            "isAuthorized": False
        }

        response = self.client.get(reverse('group-authorization', kwargs={'pk': g1.pk}))
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
