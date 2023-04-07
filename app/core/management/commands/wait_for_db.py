""""
Custom django management command.
"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Custom command to wait for the db to be ready."""

    def handle(self, *args, **options):
        pass
