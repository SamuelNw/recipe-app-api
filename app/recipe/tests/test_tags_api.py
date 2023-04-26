"""
Tests for the tags API.
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag, Recipe

from recipe.serializers import TagSerializer


TAGS_URL = reverse("recipe:tag-list")


def detail_url(tag_id):
    """Helper function to create dynamic detail urls."""
    return reverse("recipe:tag-detail", args=[tag_id])


def create_user(email="user@example.com", password="testpass123"):
    """Helper function to create a new user."""
    return get_user_model().objects.create_user(
        email=email,
        password=password
    )


class PublicTagsAPITests(TestCase):
    """Tests for unauthorized calls to the tags API."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required to list tags."""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsAPITests(TestCase):
    """Tests for authorized calls to the tags API."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_retrieving_tags_with_auth(self):
        """Test retrieving tags while authenticated works."""
        Tag.objects.create(user=self.user, name="vegan")
        Tag.objects.create(user=self.user, name="Dessert")

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by("-name")
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test that returned tags belong to the registered user."""
        new_user = create_user(
            email="newuser@example.com", password="testpass123")
        Tag.objects.create(user=new_user, name="Fruits")
        tag = Tag.objects.create(user=self.user, name="Supplements")

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(res.data[0]["name"], tag.name)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(tag.user, self.user)

    def test_update_tag(self):
        """Test that updating tags works successfully."""
        tag = Tag.objects.create(user=self.user, name="After Dinner")

        payload = {"name": "Junk"}
        url = detail_url(tag.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload["name"])
        self.assertEqual(tag.user, self.user)

    def test_delete_tag(self):
        """Test that deleting tags works."""
        tag = Tag.objects.create(user=self.user, name="Breakfast")

        url = detail_url(tag.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        tags = Tag.objects.filter(user=self.user)
        self.assertFalse(tags.exists())

    def test_filtering_tags_by_assigned(self):
        """Test filtering tags by those assigned to a recipe."""
        tag1 = Tag.objects.create(user=self.user, name="Breakfast")
        tag2 = Tag.objects.create(user=self.user, name="Lunch")
        recipe = Recipe.objects.create(
            user=self.user,
            title="Apple Crumble",
            time_in_minutes=5,
            price=Decimal("4.50")
        )
        recipe.tags.add(tag1)

        res = self.client.get(TAGS_URL, {"assigned_only": 1})

        s1 = TagSerializer(tag1)
        s2 = TagSerializer(tag2)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)
