import datetime
import json

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from ippon.models import Player, Club

BAD_PK = 0


class PlayerViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.u1 = User.objects.create(username='a1', password='password1')
        self.c1 = Club.objects.create(name='cn1', webpage='http://cw1.co', description='cd1', city='cc1')
        self.p1 = Player.objects.create(name='pn1', surname='ps1', rank=1,
                                        birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=self.c1)
        self.p2 = Player.objects.create(name='pn2', surname='ps2', rank=2,
                                        birthday=datetime.date(year=2002, month=2, day=2), sex=0, club_id=self.c1)
        self.p3 = Player.objects.create(name='pn3', surname='ps3', rank=3,
                                        birthday=datetime.date(year=2003, month=3, day=3), sex=1, club_id=self.c1)
        self.valid_payload = {
            "name": "pn7",
            "surname": "ps7",
            "rank": 7,
            "birthday": "2007-07-07",
            "sex": 1,
            "club_id": self.c1.id
        }

        self.invalid_payload = {
            "name": "cn3",
            "webpage": "http://cw3.co",
            "description": "cd3"
        }

        self.p1_json = {
            "id": self.p1.id,
            "name": "pn1",
            "surname": "ps1",
            "rank": 1,
            "birthday": "2001-01-01",
            "sex": 1,
            "club_id": self.c1.id
        }

        self.p2_json = {
            "id": self.p2.id,
            "name": "pn2",
            "surname": "ps2",
            "rank": 2,
            "birthday": "2002-02-02",
            "sex": 0,
            "club_id": self.c1.id
        }

        self.p3_json = {
            "id": self.p3.id,
            "name": "pn3",
            "surname": "ps3",
            "rank": 3,
            "birthday": "2003-03-03",
            "sex": 1,
            "club_id": self.c1.id
        }


class PlayerViewSetAuthorizedTests(PlayerViewTest):
    def setUp(self):
        super(PlayerViewSetAuthorizedTests, self).setUp()
        self.c1.admins.create(user=self.u1)
        self.client.force_authenticate(user=self.u1)

    def test_post_valid_payload_creates_specified_player(self):
        response = self.client.post(
            reverse('player-list'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_invalid_payload_returns_400(self):
        response = self.client.post(
            reverse('player-list'),
            data=json.dumps(self.invalid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_put_valid_payload_updates_player(self):
        response = self.client.put(
            reverse('player-detail', kwargs={'pk': self.p1.pk}),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.valid_payload["id"] = self.p1.id
        self.assertEqual(self.valid_payload, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_put_invalid_payload_gets_bad_request(self):
        response = self.client.put(
            reverse('player-detail', kwargs={'pk': self.p1.pk}),
            data=json.dumps(self.invalid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_existing_player_deletes_it(self):
        response = self.client.delete(reverse('player-detail', kwargs={'pk': self.p2.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_not_existing_player_returns_bad_request(self):
        response = self.client.delete(reverse('player-detail', kwargs={'pk': BAD_PK}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class PlayerViewSetUnauthorizedTests(PlayerViewTest):
    def setUp(self):
        super(PlayerViewSetUnauthorizedTests, self).setUp()
        self.client.force_authenticate(user=self.u1)

    def test_unauthorized_put_gets_forbidden(self):
        response = self.client.put(
            reverse('player-detail', kwargs={'pk': self.p1.pk}),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthorized_post_gets_forbidden(self):
        response = self.client.post(
            reverse('player-list'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthorized_delete_gets_forbidden(self):
        response = self.client.delete(reverse('player-detail', kwargs={'pk': self.p1.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class PlayerViewSetUnauthenticatedTests(PlayerViewTest):
    def setUp(self):
        super(PlayerViewSetUnauthenticatedTests, self).setUp()

    def test_list_returns_all_players(self):
        response = self.client.get(reverse('player-list'))

        self.assertEqual([self.p1_json, self.p2_json, self.p3_json], response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detail_for_existing_player_returns_correct_player(self):
        response = self.client.get(reverse('player-detail', kwargs={'pk': self.p1.pk}))
        self.assertEqual(self.p1_json, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detail_for_not_existing_player_returns_404(self):
        response = self.client.get(reverse('player-detail', kwargs={'pk': BAD_PK}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthorized_put_gets_unauthorized(self):
        response = self.client.put(
            reverse('player-detail', kwargs={'pk': self.p1.pk}),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_post_gets_unauthorized(self):
        response = self.client.post(
            reverse('player-list'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_delete_gets_unauthorized(self):
        response = self.client.delete(reverse('player-detail', kwargs={'pk': self.p1.id}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
