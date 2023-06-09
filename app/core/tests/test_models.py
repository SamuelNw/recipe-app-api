"""
Code to test models.
"""

from decimal import Decimal

from unittest.mock import patch
from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def create_user(email="test@example.com", password="testpass123"):
    """Helper function to create users."""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):
    """Test models"""

    def test_create_user_with_email_successful(self):
        """Test that creating users with emails works"""

        email = "test@example.com"
        password = "testpass123"
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test new user emails are normalized."""
        sample_emails = [
            ["test1@EXAMPLE.com", "test1@example.com"],
            ["Test2@Example.com", "Test2@example.com"],
            ["TEST3@EXAMPLE.COM", "TEST3@example.com"],
            ["test4@example.COM", "test4@example.com"],
        ]

        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test creation of users without email raises error."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user("", "test123")

    def test_create_superuser(self):
        """Test creation of a superuser."""
        user = get_user_model().objects.create_superuser(
            "test1@example.com", "test123"
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_recipe(self):
        """Test that creation of a recipe is successful."""
        user = create_user()

        recipe = models.Recipe.objects.create(
            user=user,
            title="Sample recipe title.",
            time_in_minutes=5,
            price=Decimal("5.50"),
            description="Sample recipe description",
        )

        self.assertEqual(str(recipe), recipe.title)

    def test_create_tag(self):
        """Test that creation of tags is successful."""
        user = create_user()

        tag = models.Tag.objects.create(
            user=user,
            name="Test tag.",
        )

        self.assertEqual(str(tag), tag.name)

    def test_create_ingredient(self):
        """Test that creation of ingredients is successful."""
        user = create_user()

        ingredient = models.Ingredient.objects.create(
            user=user,
            name="Ingredient1"
        )

        self.assertEqual(str(ingredient), ingredient.name)

    @patch("core.models.uuid.uuid4")
    def test_recipe_file_name_uuid(self, mock_uuid):
        """Test generating image path."""
        uuid = "test-uuid"
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None, "example.jpg")

        self.assertEqual(file_path, f"uploads/recipe/{uuid}.jpg")
