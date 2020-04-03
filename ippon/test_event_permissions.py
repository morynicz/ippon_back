import datetime

import django.test
import pytz
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient

from ippon.models import Event


class TestFightPermissions(django.test.TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="jack@ripper.com",
            username="JackTheRipper",
            password="ultrasecurepassword123",
            first_name="JackThe",
            last_name="Ripper"
        )

        self.event: Event = Event(
            name="Tournament",
            description="It's very cool",
            event_owner=self.user,
            registration_start_time=datetime.datetime.now(pytz.UTC),
            registration_end_time=datetime.datetime.now(pytz.UTC),
            start_time=datetime.datetime.now(pytz.UTC),
            end_time=datetime.datetime.now(pytz.UTC)
        )
        self.event.save()

    def test_event_get_with_unauthorized_user_return_200(self):
        response = self.client.get("/ippon/events/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_event_delete_with_unauthorized_user_return_403(self):
        response = self.client.delete(f"/ippon/events/{self.event.pk}/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_event_creation_with_unauthorized_user_return_401(self):
        response = self.client.post("/ippon/events/", {
            "name": "Cool Event",
            "description": "cool description",
            "event_owner": self.user.pk,
            "start_time": datetime.datetime.now(),
            "end_time": datetime.datetime.now(),
            "registration_start_time": datetime.datetime.now(),
            "registration_end_time": datetime.datetime.now()
        })

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_event_creation_with_valid_owner_return_201(self):
        self.client.force_authenticate(self.user)
        response = self.client.post("/ippon/events/", {
            "name": "Cool Event",
            "description": "cool description",
            "event_owner": self.user.pk,
            "start_time": datetime.datetime.now(),
            "end_time": datetime.datetime.now(),
            "registration_start_time": datetime.datetime.now(),
            "registration_end_time": datetime.datetime.now()
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_event_creation_with_invalid_owner_return_403(self):
        self.client.force_authenticate(self.user)
        response = self.client.post("/ippon/events/", {
            "name": "Cool Event",
            "description": "cool description",
            "event_owner": self.user.pk + 1,
            "start_time": datetime.datetime.now(),
            "end_time": datetime.datetime.now(),
            "registration_start_time": datetime.datetime.now(),
            "registration_end_time": datetime.datetime.now()
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_event_delete_with_valid_owner_return_200(self):
        self.client.force_authenticate(self.user)
        response = self.client.delete(f"/ippon/events/{self.event.pk}/")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)