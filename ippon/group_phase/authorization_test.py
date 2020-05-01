from django.urls.base import reverse
from rest_framework import status

import ippon.models.group_phase as gpm
import ippon.models.tournament as tm
import ippon.utils.authorization_test_fixtures as iua


class TournamentGroupPhaseAuthorizationAuthenticatedTests(iua.AuthorizationViewsAuthenticatedTests):
    def setUp(self):
        super(TournamentGroupPhaseAuthorizationAuthenticatedTests, self).setUp()
        self.group_phase = gpm.GroupPhase.objects.create(name="gp1", tournament=self.tournament, fight_length=3)

    def test_tournament_group_phase_authorization_returns_negative_auth_if_not_authorized(self):
        expected = {
            "isAuthorized": False
        }

        response = self.client.get(reverse('group-phase-authorization', kwargs={'pk': self.group_phase.pk}))
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_tournament_group_phase_authorization_returns_positive_auth_if_authorized_staff(self):
        self.parametrized_group_phase_authorization_returns_positive_auth_if_authorized(False)

    def test_tournament_group_phase_authorization_returns_positive_auth_if_authorized_admin(self):
        self.parametrized_group_phase_authorization_returns_positive_auth_if_authorized(True)

    def parametrized_group_phase_authorization_returns_positive_auth_if_authorized(self, is_admin):
        tm.TournamentAdmin.objects.create(user=self.u1, tournament=self.tournament, is_master=is_admin)
        expected = {
            "isAuthorized": True
        }
        response = self.client.get(reverse('group-phase-authorization', kwargs={'pk': self.group_phase.pk}))
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class GroupPhaseViewsUnauthenticatedTests(iua.AuthorizationViewsUnauthenticatedTests):
    def setUp(self):
        super(GroupPhaseViewsUnauthenticatedTests, self).setUp()

    def test_tournament_group_phase_authorization_returns_negative_auth_if_not_authorized(self):
        group_phase = gpm.GroupPhase.objects.create(name="gp1", tournament=self.tournament, fight_length=3)
        expected = {
            "isAuthorized": False
        }

        response = self.client.get(reverse('group-phase-authorization', kwargs={'pk': group_phase.pk}))
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
