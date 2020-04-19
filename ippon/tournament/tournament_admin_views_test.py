import datetime
import json

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

import ippon.tournament.models as tm

BAD_PK = 0


class TournamentAdminViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.u1 = User.objects.create(username='a1', password='password1')
        self.u2 = User.objects.create(username='a2', password='password2')

        self.to1 = tm.Tournament.objects.create(name='T1', webpage='http://w1.co', description='d1', city='c1',
                                                date=datetime.date(year=2021, month=1, day=1), address='a1',
                                                team_size=1, group_match_length=3, ko_match_length=3,
                                                final_match_length=3, finals_depth=0, age_constraint=5,
                                                age_constraint_value=20, rank_constraint=5, rank_constraint_value=7,
                                                sex_constraint=1)
        self.a1 = tm.TournamentAdmin.objects.create(user=self.u1, tournament=self.to1, is_master=True)

        self.valid_payload = {
            "id": -1,
            "tournament_id": self.to1.id,
            "user": {
                "id": self.u2.id,
                "username": self.u2.username
            },
            "is_master": False
        }


class TournamentAdminViewSetAuthorizedTests(TournamentAdminViewTest):
    def setUp(self):
        super(TournamentAdminViewSetAuthorizedTests, self).setUp()
        self.client.force_authenticate(user=self.u1)

    def test_creates_admin_with_valid_payload(self):
        response = self.client.post(reverse('tournamentadmin-list'),
                                    kwargs={'pk': self.to1.id},
                                    data=json.dumps(self.valid_payload),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(tm.TournamentAdmin.objects.filter(tournament=self.to1.id, user=self.u2).exists())


class TournamentAdminViewSetUnauthorizedTests(TournamentAdminViewTest):
    def setUp(self):
        super(TournamentAdminViewSetUnauthorizedTests, self).setUp()
        self.client.force_authenticate(user=self.u2)

    def test_admin_creation_attempt_gets_forbidden(self):
        response = self.client.post(reverse('tournamentadmin-list'),
                                    kwargs={'pk': self.to1.id},
                                    data=json.dumps(self.valid_payload),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(tm.TournamentAdmin.objects.filter(tournament=self.to1.id, user=self.u2).exists())


class TournamentAdminViewSetUnauthenticatedTests(TournamentAdminViewTest):
    def setUp(self):
        super(TournamentAdminViewSetUnauthenticatedTests, self).setUp()

    def test_admin_creation_attempt_gets_unauthorized(self):
        response = self.client.post(reverse('tournamentadmin-list'),
                                    kwargs={'pk': self.to1.id},
                                    data=json.dumps(self.valid_payload),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(tm.TournamentAdmin.objects.filter(tournament=self.to1.id, user=self.u2).exists())
