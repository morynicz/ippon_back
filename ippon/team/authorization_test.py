from django.urls.base import reverse
from rest_framework import status

import ippon.models.team as tem
import ippon.models.tournament as tm
import ippon.utils.authorization_test_fixtures as iua


class TournamentTeamAuthorizationAuthenticatedTests(
    iua.AuthorizationViewsAuthenticatedTests
):
    def setUp(self):
        super(TournamentTeamAuthorizationAuthenticatedTests, self).setUp()

    def test_tournament_team_authorization_returns_negative_auth_if_not_authorized(
        self,
    ):
        t1 = tem.Team.objects.create(name="t1", tournament=self.tournament)
        expected = {"isAuthorized": False}

        response = self.client.get(reverse("team-authorization", kwargs={"pk": t1.pk}))
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_tournament_team_authorization_returns_positive_auth_if_authorized_staff(
        self,
    ):
        self.parametrized_team_authorization_returns_positive_auth_if_authorized(False)

    def test_tournament_team_authorization_returns_positive_auth_if_authorized_admin(
        self,
    ):
        self.parametrized_team_authorization_returns_positive_auth_if_authorized(True)

    def parametrized_team_authorization_returns_positive_auth_if_authorized(
        self, is_admin
    ):
        tm.TournamentAdmin.objects.create(
            user=self.u1, tournament=self.tournament, is_master=is_admin
        )
        t1 = tem.Team.objects.create(name="t1", tournament=self.tournament)
        expected = {"isAuthorized": True}
        response = self.client.get(reverse("team-authorization", kwargs={"pk": t1.pk}))
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TeamViewsUnauthenticatedTests(iua.AuthorizationViewsUnauthenticatedTests):
    def setUp(self):
        super(TeamViewsUnauthenticatedTests, self).setUp()

    def test_tournament_team_authorization_returns_negative_auth(self):
        t1 = tem.Team.objects.create(name="t1", tournament=self.tournament)
        expected = {"isAuthorized": False}

        response = self.client.get(reverse("team-authorization", kwargs={"pk": t1.pk}))
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
