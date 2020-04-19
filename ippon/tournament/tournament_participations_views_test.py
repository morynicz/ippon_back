import datetime
import json

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

import ippon.tournament.models as tm
import ippon.club.models as cl

BAD_PK = 0


class TournamentParticipationsViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.club = cl.Club.objects.create(name='cn1', webpage='http://cw1.co', description='cd1', city='cc1')
        self.player = self.club.players.create(name='pn1', surname='ps1', rank=7,
                                               birthday=datetime.date(year=2001, month=1, day=1), sex=1,
                                               club_id=self.club)
        self.user = User.objects.create(username='admin', password='password')
        self.user2 = User.objects.create(username='nonadmin', password='password')
        self.to1 = tm.Tournament.objects.create(name='T1', webpage='http://w1.co', description='d1', city='c1',
                                                date=datetime.date(year=2021, month=1, day=1), address='a1',
                                                team_size=1, group_match_length=3, ko_match_length=3,
                                                final_match_length=3, finals_depth=0, age_constraint=5,
                                                age_constraint_value=20, rank_constraint=5, rank_constraint_value=7,
                                                sex_constraint=1)

        self.valid_payload = {
            "player": {"id": self.player.id,
                       "name": self.player.name,
                       "surname": self.player.surname
                       },
            "tournament_id": self.to1.id,
            "is_paid": False,
            "is_registered": False,
            "is_qualified": False,
            "is_sex_ok": False,
            "is_rank_ok": False,
            "is_age_ok": False,
            "id": 0,
            "notes": ""
        }

        self.invalid_payload = {
            "player": {"id": 35,
                       "name": "Wendy",
                       "surname": "George"
                       },
            "tournament_id": self.to1.id
        }


class TournamentParticipationViewSetAuthorizedTests(TournamentParticipationsViewTest):
    def setUp(self):
        super(TournamentParticipationViewSetAuthorizedTests, self).setUp()
        tm.TournamentAdmin.objects.create(user=self.user, tournament=self.to1, is_master=True)
        self.client.force_authenticate(user=self.user)

    def test_post_invalid_payload_returns_400(self):
        response = self.client.post(
            reverse('tournamentparticipation-list'),
            data=json.dumps(self.invalid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_valid_payload_returns_201(self):
        response = self.client.post(
            reverse('tournamentparticipation-list'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class TournamentParticipationViewSetUnauthorizedTests(TournamentParticipationsViewTest):
    def setUp(self):
        super(TournamentParticipationViewSetUnauthorizedTests, self).setUp()
        tm.TournamentAdmin.objects.create(user=self.user, tournament=self.to1, is_master=True)
        self.client.force_authenticate(user=self.user2)

    def test_post_invalid_payload_returns_403(self):
        response = self.client.post(
            reverse('tournamentparticipation-list'),
            data=json.dumps(self.invalid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_valid_payload_returns_403(self):
        response = self.client.post(
            reverse('tournamentparticipation-list'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TournamentParticipationViewSetUnauthenticatedTests(TournamentParticipationsViewTest):
    def setUp(self):
        super(TournamentParticipationViewSetUnauthenticatedTests, self).setUp()
        tm.TournamentAdmin.objects.create(user=self.user, tournament=self.to1, is_master=True)

    def test_post_invalid_payload_returns_401(self):
        response = self.client.post(
            reverse('tournamentparticipation-list'),
            data=json.dumps(self.invalid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_valid_payload_returns_201(self):
        response = self.client.post(
            reverse('tournamentparticipation-list'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
