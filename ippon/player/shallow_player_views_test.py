import datetime
import json

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

import ippon.player.models as plm
import ippon.club.models as cl

BAD_PK = 0


class ShallowPlayerViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.u1 = User.objects.create(username='a1', password='password1')
        self.c1 = cl.Club.objects.create(name='cn1', webpage='http://cw1.co', description='cd1', city='cc1')
        self.p1 = plm.Player.objects.create(name='pn1', surname='ps1', rank=1,
                                            birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=self.c1)
        self.p2 = plm.Player.objects.create(name='pn2', surname='ps2', rank=2,
                                            birthday=datetime.date(year=2002, month=2, day=2), sex=0, club_id=self.c1)
        self.p3 = plm.Player.objects.create(name='pn3', surname='ps3', rank=3,
                                            birthday=datetime.date(year=2003, month=3, day=3), sex=1, club_id=self.c1)
        self.valid_payload = {
            "name": "pn7",
            "surname": "ps7",
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
        }

        self.p2_json = {
            "id": self.p2.id,
            "name": "pn2",
            "surname": "ps2",
        }

        self.p3_json = {
            "id": self.p3.id,
            "name": "pn3",
            "surname": "ps3"
        }


class ShallowPlayerViewSetUnauthorizedTests(ShallowPlayerViewTest):
    def setUp(self):
        super(ShallowPlayerViewSetUnauthorizedTests, self).setUp()

    def test_list_returns_all_players(self):
        response = self.client.get(reverse('shallow-player-list'))

        self.assertEqual([self.p1_json, self.p2_json, self.p3_json], response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detail_for_existing_player_returns_correct_player(self):
        response = self.client.get(reverse('shallow-player-detail', kwargs={'pk': self.p1.pk}))
        self.assertEqual(self.p1_json, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detail_for_not_existing_player_returns_404(self):
        response = self.client.get(reverse('shallow-player-detail', kwargs={'pk': BAD_PK}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_put_gets_method_not_allowed(self):
        response = self.client.put(
            reverse('shallow-player-list'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_post_gets_method_not_allowed(self):
        response = self.client.post(
            reverse('shallow-player-list'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_gets_method_not_allowed(self):
        response = self.client.delete(reverse('shallow-player-detail', kwargs={'pk': self.c1.id}))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
