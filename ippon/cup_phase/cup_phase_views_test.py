import datetime
import json

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

import ippon.models.tournament as tm
import ippon.utils.values as iuv


class CupPhasesViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(username='admin', password='password')
        self.to = tm.Tournament.objects.create(name='T1', webpage='http://w1.co', description='d1', city='c1',
                                               date=datetime.date(year=2021, month=1, day=1), address='a1',
                                               team_size=1, group_match_length=3, ko_match_length=3,
                                               final_match_length=3, finals_depth=0, age_constraint=5,
                                               age_constraint_value=20, rank_constraint=5, rank_constraint_value=7,
                                               sex_constraint=1)

        self.cp1 = self.to.cup_phases.create(fight_length=3, name="cp1", final_fight_length=4, number_of_positions=16)
        self.cp2 = self.to.cup_phases.create(fight_length=5, name="cp2", final_fight_length=6, number_of_positions=15)

        self.cp1_json = {
            'id': self.cp1.id,
            'tournament': self.to.id,
            'fight_length': 3,
            'name': 'cp1',
            'final_fight_length': 4,
            'number_of_positions': 16
        }
        self.cp2_json = {
            'id': self.cp2.id,
            'tournament': self.to.id,
            'fight_length': 5,
            'name': 'cp2',
            'final_fight_length': 6,
            'number_of_positions': 15
        }
        self.valid_payload = {
            'id': self.cp1.id,
            'tournament': self.to.id,
            'fight_length': 3,
            'name': 'cp1',
            'final_fight_length': 4,
            'number_of_positions': 16
        }
        self.invalid_payload = {
            'id': self.cp1.id,
            'tournament': self.to.id,
            'fight_length': 3,
            'name': 'cp1'
        }


class CupPhasesViewSetAuthorizedTests(CupPhasesViewTest):
    def setUp(self):
        super(CupPhasesViewSetAuthorizedTests, self).setUp()
        tm.TournamentAdmin.objects.create(user=self.user, tournament=self.to, is_master=False)
        self.client.force_authenticate(user=self.user)

    def test_post_valid_payload_creates_specified_cup_phase(self):
        response = self.client.post(
            reverse('cupphase-list'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_invalid_payload_returns_400(self):
        response = self.client.post(
            reverse('cupphase-list'),
            data=json.dumps(self.invalid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_put_valid_payload_updates_cup_phase(self):
        response = self.client.put(
            reverse('cupphase-detail', kwargs={'pk': self.cp1.pk}),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        expected = self.cp1_json.copy()
        expected['fight_length'] = self.valid_payload['fight_length']
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_put_invalid_payload_gets_bad_request(self):
        response = self.client.put(
            reverse('cupphase-detail', kwargs={'pk': self.cp1.pk}),
            data=json.dumps(self.invalid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_existing_cup_phase_deletes_it(self):
        response = self.client.delete(reverse('cupphase-detail', kwargs={'pk': self.cp1.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_not_existing_cup_phase_returns_bad_request(self):
        response = self.client.delete(reverse('cupphase-detail', kwargs={'pk': -5}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CupPhaseViewSetUnauthorizedTests(CupPhasesViewTest):
    def setUp(self):
        super(CupPhaseViewSetUnauthorizedTests, self).setUp()
        self.client.force_authenticate(user=self.user)

    def test_unauthorized_put_gets_forbidden(self):
        response = self.client.put(
            reverse('cupphase-detail', kwargs={"pk": self.cp1.pk}),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthorized_post_gets_forbidden(self):
        response = self.client.post(
            reverse('cupphase-list'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthorized_delete_gets_forbidden(self):
        response = self.client.delete(reverse('cupphase-detail', kwargs={'pk': self.cp1.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CupPhaseViewSetUnauthenticatedTests(CupPhasesViewTest):
    def setUp(self):
        super(CupPhaseViewSetUnauthenticatedTests, self).setUp()

    def test_list_returns_all_cup_phases(self):
        response = self.client.get(reverse('cupphase-list'))

        self.assertEqual([self.cp1_json, self.cp2_json], response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detail_for_existing_cup_phase_returns_correct_cup_phase(self):
        response = self.client.get(reverse('cupphase-detail', kwargs={'pk': self.cp1.pk}))
        self.assertEqual(self.cp1_json, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detail_for_not_existing_cup_phase_returns_404(self):
        response = self.client.get(reverse('cupphase-detail', kwargs={'pk': -1}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthorized_put_gets_unauthorized(self):
        response = self.client.post(
            reverse('cupphase-list'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_delete_gets_unauthorized(self):
        response = self.client.delete(reverse('cupphase-detail', kwargs={'pk': self.cp1.id}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_fights_for_valid_cup_phase_returns_list_of_cup_fights(self):
        team1 = self.to.teams.create(name='t1')
        team2 = self.to.teams.create(name='t2')
        team3 = self.to.teams.create(name='t3')
        team4 = self.to.teams.create(name='t4')
        tf1 = self.to.team_fights.create(aka_team=team1, shiro_team=team2)
        tf2 = self.to.team_fights.create(aka_team=team3, shiro_team=team4)
        cf1 = self.cp1.cup_fights.create(team_fight=tf1)
        cf2 = self.cp1.cup_fights.create(team_fight=tf2)
        cf3 = self.cp1.cup_fights.create(previous_shiro_fight=cf1, previous_aka_fight=cf2)

        cf1_json = {'id': cf1.id, "cup_phase": self.cp1.id, "team_fight": tf1.id, 'previous_shiro_fight': None,
                    'previous_aka_fight': None}
        cf2_json = {'id': cf2.id, "cup_phase": self.cp1.id, "team_fight": tf2.id, 'previous_shiro_fight': None,
                    'previous_aka_fight': None}
        cf3_json = {'id': cf3.id, "cup_phase": self.cp1.id, "team_fight": None, 'previous_shiro_fight': cf1.id,
                    'previous_aka_fight': cf2.id}

        expected = [cf1_json, cf2_json, cf3_json]
        response = self.client.get(reverse('cupphase-cup_fights', kwargs={'pk': self.cp1.pk}))
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_fights_for_invalid_cup_phase_returns_not_found(self):
        response = self.client.get(reverse('cupphase-cup_fights', kwargs={'pk': iuv.BAD_PK}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
