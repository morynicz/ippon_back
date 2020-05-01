from django.urls import reverse
from rest_framework import status

import ippon.utils.authorization_test_fixtures as iua


class ClubAuthorizationAuthenticatedTests(iua.AuthorizationViewsAuthenticatedTests):
    def setUp(self):
        super(ClubAuthorizationAuthenticatedTests, self).setUp()

    def test_club_authorization_returns_positive_auth_if_authorized(self):
        expected = {
            "isAuthorized": True
        }

        response = self.client.get(reverse('club-authorization', kwargs={'pk': self.c1.pk}))
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_club_authorization_returns_negative_auth_if_not_authorized(self):
        expected = {
            "isAuthorized": False
        }

        response = self.client.get(reverse('club-authorization', kwargs={'pk': self.c2.pk}))
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class PlayerAuthorizationAuthenticatedTests(iua.AuthorizationViewsAuthenticatedTests):
    def setUp(self):
        super(PlayerAuthorizationAuthenticatedTests, self).setUp()

    def test_player_authorization_returns_positive_auth_if_authorized(self):
        expected = {
            "isAuthorized": True
        }

        response = self.client.get(reverse('player-authorization', kwargs={'pk': self.p1.pk}))
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_player_authorization_returns_negative_auth_if_not_authorized(self):
        expected = {
            "isAuthorized": False
        }

        response = self.client.get(reverse('player-authorization', kwargs={'pk': self.p2.pk}))
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ClubAuthorizationUnauthenticatedTests(iua.AuthorizationViewsUnauthenticatedTests):
    def setUp(self):
        super(ClubAuthorizationUnauthenticatedTests, self).setUp()

    def test_club_authorization_returns_negative_auth_if_not_authenticated(self):
        expected = {
            "isAuthorized": False
        }

        response = self.client.get(reverse('club-authorization', kwargs={'pk': self.c1.pk}))
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class PlayerAuthorizationUnauthenticatedTests(iua.AuthorizationViewsUnauthenticatedTests):
    def setUp(self):
        super(PlayerAuthorizationUnauthenticatedTests, self).setUp()

    def test_player_authorization_returns_negative_auth_if_not_authenticated(self):
        expected = {
            "isAuthorized": False
        }

        response = self.client.get(reverse('player-authorization', kwargs={'pk': self.p1.pk}))
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
