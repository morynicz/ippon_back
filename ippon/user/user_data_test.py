from django.contrib.auth.models import User
from django.urls import reverse
from requests import Response
from rest_framework import status
from rest_framework.test import APITestCase, APIClient


class UserDataViewTest(APITestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_invalid_user_responds_with_401_and_error_message(self):
        response: Response = self.client.get(reverse("user-data"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data, {
            "error": "You are not logged in."
        })

    def test_valid_user_responds_with_200_and_correct_data(self):
        self.user = User.objects.create_user(
            email="jack@ripper.com",
            username="JackTheRipper",
            password="ultrasecurepassword123",
            first_name="JackThe",
            last_name="Ripper"
        )
        self.client.force_authenticate(self.user)

        response: Response = self.client.get(reverse("user-data"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            "id": self.user.id,
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            "username": self.user.username,
            "email": self.user.email
        })
