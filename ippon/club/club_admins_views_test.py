import json
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

import ippon.models.club as cl


class ClubAdminViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.u1 = User.objects.create(username="a1", password="password1")
        self.u2 = User.objects.create(username="a2", password="password2")

        self.c1 = cl.Club.objects.create(name="cn1", webpage="http://cw1.co", description="cd1", city="cc1")
        self.a1 = cl.ClubAdmin.objects.create(user=self.u1, club=self.c1)

        self.valid_payload = {
            "id": -1,
            "club_id": self.c1.id,
            "user": {"id": self.u2.id, "username": self.u2.username},
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


class ClubAdminViewSetAuthorizedTests(ClubAdminViewTest):
    def setUp(self):
        super(ClubAdminViewSetAuthorizedTests, self).setUp()
        self.client.force_authenticate(user=self.u1)

    def test_creates_admin_with_valid_payload(self):
        response = self.client.post(
            reverse("clubadmin-list"),
            kwargs={"pk": self.c1.id},
            data=json.dumps(self.valid_payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(cl.ClubAdmin.objects.filter(club=self.c1.id, user=self.u2).exists())


class ClubAdminViewSetUnauthorizedTests(ClubAdminViewTest):
    def setUp(self):
        super(ClubAdminViewSetUnauthorizedTests, self).setUp()
        self.client.force_authenticate(user=self.u2)

    def test_admin_creation_attempt_gets_forbidden(self):
        response = self.client.post(
            reverse("clubadmin-list"),
            kwargs={"pk": self.c1.id},
            data=json.dumps(self.valid_payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(cl.ClubAdmin.objects.filter(club=self.c1.id, user=self.u2).exists())


class ClubAdminViewSetUnauthenticatedTests(ClubAdminViewTest):
    def setUp(self):
        super(ClubAdminViewSetUnauthenticatedTests, self).setUp()

    def test_admin_creation_attempt_gets_unauthorized(self):
        response = self.client.post(
            reverse("clubadmin-list"),
            kwargs={"pk": self.c1.id},
            data=json.dumps(self.valid_payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(cl.ClubAdmin.objects.filter(club=self.c1.id, user=self.u2).exists())
