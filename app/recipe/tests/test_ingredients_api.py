"""
Tests for the ingredients API.
"""

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient

from recipe.serializers import IngredientSerializer


INGREDIENTS_URL = reverse("recipe:ingredient-list")


def create_user(email="user@example.com", password="testpass123"):
    """Helper function to create a new user."""
    return get_user_model().objects.create_user(
        email=email, passowrd=password)


class PublicIngredientAPITests(TestCase):
    """Tests for unauthenticated calls to the endpoint."""

    def setUp(self):
        self.client = APIClient()

    def test_authentication_required(self):
        """Test authentication required to obtain ingredients."""
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientAPITests(TestCase):
    """Test authenticated calls to the endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_retrieving_ingredients(self):
        """Test that authenticated users retrieve ingredients."""
        Ingredient.objects.create(user=self.user, name="Kale")
        Ingredient.objects.create(user=self.user, name="Vanilla")

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        ingredients = Ingredient.objects.all().order_by("-name")
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(len(ingredients), 2)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test that a user only retrieves their ingredients."""
        user2 = create_user(email="user2@example.com")
        Ingredient.objects.create(user=user2, name="Spices")
        ingredient = Ingredient.objects.create(
            user=self.user, name="Toppings")

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        ingredients = Ingredient.objects.all().order_by("-name")
        self.assertEqual(len(ingredients), 1)
        self.assertEqual(ingredients[0]["name"], ingredient.name)
        self.assertEqual(ingredients[0]["user"], self.user)
