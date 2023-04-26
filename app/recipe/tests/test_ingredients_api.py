"""
Tests for the ingredients API.
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (Ingredient, Recipe)

from recipe.serializers import IngredientSerializer


INGREDIENTS_URL = reverse("recipe:ingredient-list")


def detail_url(ingredient_id):
    """Handle creation of dynamic urls."""
    return reverse("recipe:ingredient-detail", args=[ingredient_id])


def create_user(email="user@example.com", password="testpass123"):
    """Helper function to create a new user."""
    return get_user_model().objects.create_user(
        email=email, password=password)


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

        ingredients = Ingredient.objects.filter(user=self.user)
        self.assertEqual(len(ingredients), 1)
        self.assertEqual(ingredients[0].name, ingredient.name)
        self.assertEqual(ingredients[0].user, self.user)

    def test_upadating_ingredient(self):
        """Test that updating ingredient works successfully."""
        ingredient = Ingredient.objects.create(
            user=self.user, name="Cilantro")

        payload = {"name": "Coriander"}
        url = detail_url(ingredient.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, payload["name"])

    def test_deleting_ingredient(self):
        """Test deleting ingredients."""
        ingredient = Ingredient.objects.create(user=self.user, name="Spice")

        url = detail_url(ingredient.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        ingredients = Ingredient.objects.filter(user=self.user)
        self.assertFalse(ingredients.exists())

    def test_filtering_ingredients_by_assigned(self):
        """Test filtering ingredients by those assigned to a recipe."""
        in1 = Ingredient.objects.create(user=self.user, name="Apples")
        in2 = Ingredient.objects.create(user=self.user, name="Turkey")
        recipe = Recipe.objects.create(
            user=self.user,
            title="Apple Crumble",
            time_in_minutes=5,
            price=Decimal("4.50")
        )
        recipe.ingredients.add(in1)

        res = self.client.get(INGREDIENTS_URL, {"assigned_only": 1})

        s1 = IngredientSerializer(in1)
        s2 = IngredientSerializer(in2)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)
