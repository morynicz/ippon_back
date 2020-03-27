from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.utils import json


class RegistrationViewsetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.valid_payload = {
            "email": "email@email.com",
            "username": "user1",
            "password": "longandcomplicated"
        }

        self.invalid_email_payload = {
            "email": "emailemail.com",
            "username": "user1",
            "password": "longandcomplicated"
        }

        self.unique_name_error = b'["A user with that username already exists."]'
        self.email_error = b'["Enter a valid email address."]'

    @patch('django.contrib.auth.models.User.email_user')
    def test_register_unique_user_with_valid_payload_creates_new_user(self, email_user_mock):
        response = self.client.post(reverse('register-user'),
                                    data=json.dumps(self.valid_payload),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email=self.valid_payload["email"], username=self.valid_payload["username"])
        self.assertIsNotNone(user)
        self.assertTrue(user.check_password(self.valid_payload["password"]))
        email_user_mock.assert_called_with(
            subject="You have been registered",
            message="You have been successfully registered in ippon with username {}".format(
                self.valid_payload["username"]))

    def test_non_unique_username_response(self):
        User.objects.create_user(
            username=self.valid_payload["username"],
            email='a' + self.valid_payload["email"],
            password=self.valid_payload["password"])
        response = self.client.post(reverse('register-user'),
                                    data=json.dumps(self.valid_payload),
                                    content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.content, self.unique_name_error)

    def test_invalid_email_format_response(self):
        response = self.client.post(reverse('register-user'),
                                    data=json.dumps(self.invalid_email_payload),
                                    content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.content, self.email_error)
