""""
Custom django management command.
"""

import time

from psycopg2 import OperationalError as Psycopg2Error

from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Custom command to wait for the db to be ready."""

    def handle(self, *args, **options):
        """Command entrypoint."""
        self.stdout.write("Waiting for database...")
        db_up = False

        while db_up == False:
            try:
                self.check(databases=['default'])
                db_up = True
            except (Psycopg2Error, OperationalError):
                self.stdout.write('Database unavailable, waiting 1 second...')
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('Database is ready!'))
