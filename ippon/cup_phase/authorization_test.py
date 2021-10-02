from django.urls.base import reverse
from rest_framework import status

import ippon.models.cup_phase as cpm
import ippon.models.tournament as tm
import ippon.utils.authorization_test_fixtures as iua


class TournamentCupPhaseAuthorizationAuthenticatedTests(
    iua.AuthorizationViewsAuthenticatedTests
):
    def setUp(self):
        super(TournamentCupPhaseAuthorizationAuthenticatedTests, self).setUp()
        self.cup_phase = cpm.CupPhase.objects.create(
            name="cp1", tournament=self.tournament, fight_length=3, final_fight_length=5
        )

    def test_tournament_cup_phase_authorization_returns_negative_auth_if_not_authorized(
        self,
    ):
        expected = {"isAuthorized": False}

        response = self.client.get(
            reverse("cup-phase-authorization", kwargs={"pk": self.cup_phase.pk})
        )
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_tournament_cup_phase_authorization_returns_positive_auth_if_authorized_staff(
        self,
    ):
        self.parametrized_cup_phase_authorization_returns_positive_auth_if_authorized(
            False
        )

    def test_tournament_cup_phase_authorization_returns_positive_auth_if_authorized_admin(
        self,
    ):
        self.parametrized_cup_phase_authorization_returns_positive_auth_if_authorized(
            True
        )

    def parametrized_cup_phase_authorization_returns_positive_auth_if_authorized(
        self, is_admin
    ):
        tm.TournamentAdmin.objects.create(
            user=self.u1, tournament=self.tournament, is_master=is_admin
        )
        expected = {"isAuthorized": True}
        response = self.client.get(
            reverse("cup-phase-authorization", kwargs={"pk": self.cup_phase.pk})
        )
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CupPhaseViewsUnauthenticatedTests(iua.AuthorizationViewsUnauthenticatedTests):
    def setUp(self):
        super(CupPhaseViewsUnauthenticatedTests, self).setUp()

    def test_tournament_cup_phase_authorization_returns_negative_auth_if_not_authorized(
        self,
    ):
        cup_phase = cpm.CupPhase.objects.create(
            name="cp1", tournament=self.tournament, fight_length=3, final_fight_length=5
        )
        expected = {"isAuthorized": False}

        response = self.client.get(
            reverse("cup-phase-authorization", kwargs={"pk": cup_phase.pk})
        )
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
