from django.urls.base import reverse
from rest_framework import status

import ippon.models.team as tem
import ippon.models.team_fight as tfm
import ippon.models.tournament as tm
import ippon.utils.authorization_test_fixtures as iua


class TournamentTeamFightAuthorizationAuthenticatedTests(iua.AuthorizationViewsAuthenticatedTests):
    def setUp(self):
        super(TournamentTeamFightAuthorizationAuthenticatedTests, self).setUp()

    def test_tournament_team_fight_authorization_returns_negative_auth_if_not_authorized(
        self,
    ):
        t1 = tem.Team.objects.create(name="t1", tournament=self.tournament)
        t2 = tem.Team.objects.create(name="t2", tournament=self.tournament)
        tf = tfm.TeamFight.objects.create(tournament=self.tournament, aka_team=t1, shiro_team=t2)
        expected = {"isAuthorized": False}

        response = self.client.get(reverse("team-fight-authorization", kwargs={"pk": tf.pk}))
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_tournament_team_fight_authorization_returns_positive_auth_if_authorized_staff(
        self,
    ):
        self.parametrized_team_fight_authorization_returns_positive_auth_if_authorized(False)

    def test_tournament_team_fight_authorization_returns_positive_auth_if_authorized_admin(
        self,
    ):
        self.parametrized_team_fight_authorization_returns_positive_auth_if_authorized(True)

    def parametrized_team_fight_authorization_returns_positive_auth_if_authorized(self, is_admin):
        tm.TournamentAdmin.objects.create(user=self.u1, tournament=self.tournament, is_master=is_admin)
        t1 = tem.Team.objects.create(name="t1", tournament=self.tournament)
        t2 = tem.Team.objects.create(name="t2", tournament=self.tournament)
        tf = tfm.TeamFight.objects.create(tournament=self.tournament, aka_team=t1, shiro_team=t2)
        expected = {"isAuthorized": True}
        response = self.client.get(reverse("team-fight-authorization", kwargs={"pk": tf.pk}))
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TeamFightViewsUnauthenticatedTests(iua.AuthorizationViewsUnauthenticatedTests):
    def setUp(self):
        super(TeamFightViewsUnauthenticatedTests, self).setUp()

    def test_tournament_team_fight_authorization_returns_negative_auth(self):
        t1 = tem.Team.objects.create(name="t1", tournament=self.tournament)
        t2 = tem.Team.objects.create(name="t2", tournament=self.tournament)
        tf = tfm.TeamFight.objects.create(tournament=self.tournament, aka_team=t1, shiro_team=t2)
        expected = {"isAuthorized": False}

        response = self.client.get(reverse("team-fight-authorization", kwargs={"pk": tf.pk}))
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
