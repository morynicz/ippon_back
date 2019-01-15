import datetime
import json

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from ippon.models import TournamentAdmin, Tournament

BAD_PK = 0


class GroupPhasesViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(username='admin', password='password')
        self.to = Tournament.objects.create(name='T1', webpage='http://w1.co', description='d1', city='c1',
                                            date=datetime.date(year=2021, month=1, day=1), address='a1',
                                            team_size=1, group_match_length=3, ko_match_length=3,
                                            final_match_length=3, finals_depth=0, age_constraint=5,
                                            age_constraint_value=20, rank_constraint=5, rank_constraint_value=7,
                                            sex_constraint=1)

        self.gp1 = self.to.group_phases.create(fight_length=3, name="gp1")
        self.gp2 = self.to.group_phases.create(fight_length=5, name="gp2")

        self.gp1_json = {'id': self.gp1.id, 'tournament': self.to.id, 'fight_length': 3, "name": "gp1"}
        self.gp2_json = {'id': self.gp2.id, 'tournament': self.to.id, 'fight_length': 5, "name": "gp2"}
        self.valid_payload = {'id': self.gp1.id, 'tournament': self.to.id, 'fight_length': 3, "name": "gp1"}
        self.invalid_payload = {'id': self.gp1.id, 'tournament': self.to.id}


class GroupPhasesViewSetAuthorizedTests(GroupPhasesViewTest):
    def setUp(self):
        super(GroupPhasesViewSetAuthorizedTests, self).setUp()
        TournamentAdmin.objects.create(user=self.user, tournament=self.to, is_master=False)
        self.client.force_authenticate(user=self.user)

    def test_post_valid_payload_creates_specified_group_phase(self):
        response = self.client.post(
            reverse('groupphase-list'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_invalid_payload_returns_400(self):
        response = self.client.post(
            reverse('groupphase-list'),
            data=json.dumps(self.invalid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_put_valid_payload_updates_group_phase(self):
        response = self.client.put(
            reverse('groupphase-detail', kwargs={'pk': self.gp1.pk}),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        expected = self.gp1_json.copy()
        expected['fight_length'] = self.valid_payload['fight_length']
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_put_invalid_payload_gets_bad_request(self):
        response = self.client.put(
            reverse('groupphase-detail', kwargs={'pk': self.gp1.pk}),
            data=json.dumps(self.invalid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_existing_group_phase_deletes_it(self):
        response = self.client.delete(reverse('groupphase-detail', kwargs={'pk': self.gp1.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_not_existing_group_phase_returns_bad_request(self):
        response = self.client.delete(reverse('groupphase-detail', kwargs={'pk': -5}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class GroupPhaseViewSetUnauthorizedTests(GroupPhasesViewTest):
    def setUp(self):
        super(GroupPhaseViewSetUnauthorizedTests, self).setUp()
        self.client.force_authenticate(user=self.user)

    def test_put_gets_forbidden(self):
        response = self.client.put(
            reverse('groupphase-detail', kwargs={'pk': self.gp1.pk}),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_gets_forbidden(self):
        response = self.client.post(
            reverse('groupphase-list'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_gets_forbidden(self):
        response = self.client.delete(reverse('groupphase-detail', kwargs={'pk': self.gp1.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class GroupPhaseViewSetUnauthenticatedTests(GroupPhasesViewTest):
    def setUp(self):
        super(GroupPhaseViewSetUnauthenticatedTests, self).setUp()

    def test_list_returns_all_group_phases(self):
        response = self.client.get(reverse('groupphase-list'))

        self.assertEqual([self.gp1_json, self.gp2_json], response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detail_for_existing_group_phase_returns_correct_group_phase(self):
        response = self.client.get(reverse('groupphase-detail', kwargs={'pk': self.gp1.pk}))
        self.assertEqual(self.gp1_json, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detail_for_not_existing_group_phase_returns_404(self):
        response = self.client.get(reverse('groupphase-detail', kwargs={'pk': BAD_PK}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthorized_put_gets_unauthorized(self):
        response = self.client.put(
            reverse('groupphase-detail', kwargs={'pk': self.gp1.pk}),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_post_gets_unauthorized(self):
        response = self.client.post(
            reverse('groupphase-list'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_delete_gets_unauthorized(self):
        response = self.client.delete(reverse('groupphase-detail', kwargs={'pk': self.gp1.id}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_groups_for_valid_group_phase_returns_list_of_groups(self):
        group1 = self.gp1.groups.create(name='G1')
        group2 = self.gp1.groups.create(name='G2')
        g1_json = {'id': group1.id, "name": "G1", "group_phase": self.gp1.id}
        g2_json = {'id': group2.id, "name": "G2", "group_phase": self.gp1.id}

        expected = [g1_json, g2_json]
        response = self.client.get(reverse('groupphase-groups', kwargs={'pk': self.gp1.pk}))
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_groups_for_invalid_group_phase_returns_not_found(self):
        response = self.client.get(reverse('groupphase-groups', kwargs={'pk': BAD_PK}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
