"""
Tests for the user api
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse("user:create")
TOKEN_URL = reverse("user:token")
ME_URL = reverse("user:me")


def create_user(**params):
    """Helper fn to create users."""
    return get_user_model().objects.create(**params)


class PublicUserApiTests(TestCase):
    """Tests for unauthenticated actions in the user api."""

    def setUp(self):
        self.client = APIClient()

    def test_user_create_success(self):
        """Test that users are created successfully."""
        payload = {
            "email": "test@example.com",
            "password": "testpass123",
            "name": "Test Name"
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload["email"])
        self.assertTrue(user.check_password(payload["password"]))
        self.assertNotIn("password", res.data)

    def test_user_already_exists_error(self):
        """Test that the appropriate error is thrown if user exists."""
        payload = {
            "email": "test@example.com",
            "password": "testpass123",
            "name": "Test Name"
        }

        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Test that short passwords are unnacceptable."""
        payload = {
            "email": "test@example.com",
            "password": "pw",
            "name": "Test Name"
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload["email"]
        ).exists()
        self.assertFalse(user_exists)

    # def test_generates_user_tokens_successfully(self):
    #     """Test generation of tokens for valid credentials."""
    #     user_details = {
    #         "email": "test@example.com",
    #         "password": "test-password123",
    #         "name": "Test Name"
    #     }

    #     create_user(**user_details)
    #     payload = {
    #         "email": user_details["email"],
    #         "password": user_details["password"]
    #     }
    #     res = self.client.post(TOKEN_URL, payload)

    #     self.assertIn("token", res.data)
    #     self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_tokens_invalid_credentials(self):
        """Test token generation for bad credentials."""
        user_details = {
            "email": "test@example.com",
            "password": "test-password123",
            "name": "Test Name"
        }

        create_user(**user_details)
        payload = {
            "email": user_details["email"],
            "password": "badpassword"
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("token", res.data)

    def test_create_tokens_blank_password(self):
        """Test token generation for blank passwords."""
        payload = {"email": "test@example.com", "password": ""}
        res = self.client.post(TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("token", res.data)

    def test_retrieve_user_unauthorized(self):
        """Test authentication is required for users."""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Tests that require authentication."""
    pass
