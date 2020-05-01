from django.urls.base import reverse
from rest_framework import status

import ippon.utils.authorization_test_fixtures as iua
import ippon.models.tournament as tm


class TournamentAdminAuthenticatedTests(iua.AuthorizationViewsAuthenticatedTests):
    def setUp(self):
        super(TournamentAdminAuthenticatedTests, self).setUp()

    def test_tournament_admin_authorization_returns_positive_auth_if_authorized(self):
        tm.TournamentAdmin.objects.create(user=self.u1, tournament=self.tournament, is_master=True)

        expected = {
            "isAuthorized": True
        }

        response = self.client.get(reverse('tournament-admin-authorization', kwargs={'pk': self.tournament.id}))
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_tournament_staff_authorization_returns_positive_auth_if_authorized(self):
        tm.TournamentAdmin.objects.create(user=self.u1, tournament=self.tournament, is_master=False)

        expected = {
            "isAuthorized": True
        }

        response = self.client.get(reverse('tournament-staff-authorization', kwargs={'pk': self.tournament.id}))
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_tournament_admin_authorization_returns_negative_auth_if_not_authorized(self):
        expected = {
            "isAuthorized": False
        }

        response = self.client.get(reverse('tournament-admin-authorization', kwargs={'pk': self.tournament.pk}))
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_tournament_staff_authorization_returns_negative_auth_if_not_authorized(self):
        expected = {
            "isAuthorized": False
        }

        response = self.client.get(reverse('tournament-staff-authorization', kwargs={'pk': self.tournament.pk}))
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AdminViewsUnauthenticatedTests(iua.AuthorizationViewsUnauthenticatedTests):
    def setUp(self):
        super(AdminViewsUnauthenticatedTests, self).setUp()

    def test_tournament_admin_authorization_returns_negative_auth_if_not_authenticated(self):
        expected = {
            "isAuthorized": False
        }

        response = self.client.get(reverse('tournament-admin-authorization', kwargs={'pk': self.tournament.pk}))
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_tournament_staff_authorization_returns_negative_auth_if_not_authenticated(self):
        expected = {
            "isAuthorized": False
        }

        response = self.client.get(reverse('tournament-staff-authorization', kwargs={'pk': self.tournament.pk}))
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
