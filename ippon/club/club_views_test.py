import datetime
import json
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

import ippon.models.club as cl
import ippon.models.player as plm


class ClubViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.u1 = User.objects.create(username="a1", password="password1")
        self.u2 = User.objects.create(username="a2", password="password2")
        self.u3 = User.objects.create(username="u3", password="password1")

        self.c1 = cl.Club.objects.create(name="cn1", webpage="http://cw1.co", description="cd1", city="cc1")
        self.c2 = cl.Club.objects.create(name="cn2", webpage="http://cw2.co", description="cd2", city="cc2")
        self.c4 = cl.Club.objects.create(name="cn4", webpage="http://cw4.co", description="cd4", city="cc4")
        self.a1 = cl.ClubAdmin.objects.create(user=self.u1, club=self.c1)
        self.a2 = cl.ClubAdmin.objects.create(user=self.u1, club=self.c2)
        self.p1 = plm.Player.objects.create(
            name="pn1",
            surname="ps1",
            rank=7,
            birthday=datetime.date(year=2001, month=1, day=1),
            sex=1,
            club_id=self.c1,
        )
        self.p2 = plm.Player.objects.create(
            name="pn2",
            surname="ps2",
            rank=7,
            birthday=datetime.date(year=2001, month=1, day=1),
            sex=1,
            club_id=self.c1,
        )
        self.p3 = plm.Player.objects.create(
            name="pn3",
            surname="ps3",
            rank=7,
            birthday=datetime.date(year=2001, month=1, day=1),
            sex=1,
            club_id=self.c1,
        )
        self.p4 = plm.Player.objects.create(
            name="pn4",
            surname="ps4",
            rank=7,
            birthday=datetime.date(year=2001, month=1, day=1),
            sex=1,
            club_id=self.c4,
        )
        self.valid_payload = {
            "name": "cn3",
            "webpage": "http://cw1.co",
            "description": "cd1",
            "city": "cc1",
        }

        self.invalid_payload = {
            "name": "cn3",
            "webpage": "http://cw3.co",
            "description": "cd3",
        }

        self.c1_json = {
            "id": self.c1.id,
            "name": "cn1",
            "webpage": "http://cw1.co",
            "description": "cd1",
            "city": "cc1",
        }

        self.c2_json = {
            "id": self.c2.id,
            "name": "cn2",
            "webpage": "http://cw2.co",
            "description": "cd2",
            "city": "cc2",
        }
        self.c4_json = {
            "id": self.c4.id,
            "name": "cn4",
            "webpage": "http://cw4.co",
            "description": "cd4",
            "city": "cc4",
        }


class ClubViewSetAuthorizedTests(ClubViewTest):
    def setUp(self):
        super(ClubViewSetAuthorizedTests, self).setUp()
        self.client.force_authenticate(user=self.u1)

    def test_post_valid_payload_creates_specified_club(self):
        response = self.client.post(
            reverse("club-list"),
            data=json.dumps(self.valid_payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_newly_created_club_has_creator_as_admin(self):
        response = self.client.post(
            reverse("club-list"),
            data=json.dumps(self.valid_payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(cl.ClubAdmin.objects.filter(club__id=response.data["id"], user=self.u1))

    def test_post_invalid_payload_returns_400(self):
        response = self.client.post(
            reverse("club-list"),
            data=json.dumps(self.invalid_payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_put_valid_payload_updates_club(self):
        response = self.client.put(
            reverse("club-detail", kwargs={"pk": self.c1.pk}),
            data=json.dumps(self.valid_payload),
            content_type="application/json",
        )
        expected = self.c1_json.copy()
        expected["name"] = self.valid_payload["name"]
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_put_invalid_payload_gets_bad_request(self):
        response = self.client.put(
            reverse("club-detail", kwargs={"pk": self.c1.pk}),
            data=json.dumps(self.invalid_payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_existing_club_deletes_it(self):
        response = self.client.delete(reverse("club-detail", kwargs={"pk": self.c2.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_not_existing_club_returns_bad_request(self):
        response = self.client.delete(reverse("club-detail", kwargs={"pk": -5}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_players_lists_all_club_members(self):
        players = [
            {
                "id": self.p1.id,
                "name": "pn1",
                "surname": "ps1",
                "rank": 7,
                "birthday": "2001-01-01",
                "sex": 1,
                "club_id": self.c1.id,
            },
            {
                "id": self.p2.id,
                "name": "pn2",
                "surname": "ps2",
                "rank": 7,
                "birthday": "2001-01-01",
                "sex": 1,
                "club_id": self.c1.id,
            },
            {
                "id": self.p3.id,
                "name": "pn3",
                "surname": "ps3",
                "rank": 7,
                "birthday": "2001-01-01",
                "sex": 1,
                "club_id": self.c1.id,
            },
        ]
        response = self.client.get(reverse("club-players", kwargs={"pk": self.c1.id}))
        self.assertCountEqual(players, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # TODO: Change this to sending only list of users
    def test_admins_lists_all_club_admins(self):
        admin = cl.ClubAdmin.objects.create(user=self.u2, club=self.c1)
        admins = [
            {
                "id": self.a1.id,
                "club_id": self.c1.id,
                "user": {"id": self.u1.id, "username": "a1"},
            },
            {
                "id": admin.id,
                "club_id": self.c1.id,
                "user": {"id": self.u2.id, "username": "a2"},
            },
        ]
        response = self.client.get(reverse("club-admins", kwargs={"pk": self.c1.id}))

        self.assertCountEqual(admins, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_admins_lists_all_users_besides_club_admins(self):
        non_admins = [
            {"id": self.u3.id, "username": "u3"},
            {"id": self.u2.id, "username": "a2"},
        ]
        response = self.client.get(reverse("club-non-admins", kwargs={"pk": self.c1.id}))

        self.assertCountEqual(non_admins, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ClubViewSetUnauthorizedTests(ClubViewTest):
    def setUp(self):
        super(ClubViewSetUnauthorizedTests, self).setUp()
        self.client.force_authenticate(user=self.u2)

    def test_put_gets_unauthorized(self):
        response = self.client.put(
            reverse("club-detail", kwargs={"pk": self.c1.pk}),
            data=json.dumps(self.valid_payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_gets_unauthorized(self):
        response = self.client.delete(reverse("club-detail", kwargs={"pk": self.c1.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admins_returns_forbidden(self):
        response = self.client.get(reverse("club-admins", kwargs={"pk": self.c1.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_admins_returns_forbidden(self):
        response = self.client.get(reverse("club-non-admins", kwargs={"pk": self.c1.id}))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ClubViewSetUnauthenticatedTests(ClubViewTest):
    def setUp(self):
        super(ClubViewSetUnauthenticatedTests, self).setUp()

    def test_list_returns_all_clubs(self):
        response = self.client.get(reverse("club-list"))

        self.assertEqual([self.c1_json, self.c2_json, self.c4_json], response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detail_for_existing_club_returns_correct_club(self):
        response = self.client.get(reverse("club-detail", kwargs={"pk": self.c1.pk}))
        self.assertEqual(self.c1_json, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detail_for_not_existing_club_returns_404(self):
        response = self.client.get(reverse("club-detail", kwargs={"pk": -1}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthorized_post_gets_unauthorized(self):
        response = self.client.post(
            reverse("club-list"),
            data=json.dumps(self.valid_payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_put_gets_unauthorized(self):
        response = self.client.put(
            reverse("club-detail", kwargs={"pk": self.c1.pk}),
            data=json.dumps(self.valid_payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_teams_unauthorized_delete_gets_unauthorized(self):
        response = self.client.delete(reverse("club-detail", kwargs={"pk": self.c1.id}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_admins_returns_unauthorized(self):
        cl.ClubAdmin.objects.create(user=self.u2, club=self.c1)
        response = self.client.get(reverse("club-admins", kwargs={"pk": self.c1.id}))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_admins_returns_unauthorized(self):
        response = self.client.get(reverse("club-non-admins", kwargs={"pk": self.c1.id}))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
