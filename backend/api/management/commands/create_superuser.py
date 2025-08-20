"""
Management command to create a Django superuser for admin access.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = "Create a Django superuser for admin access"

    def add_arguments(self, parser):
        parser.add_argument(
            "--username", type=str, default="admin", help="Username for the superuser"
        )
        parser.add_argument(
            "--email",
            type=str,
            default="admin@grocery.com",
            help="Email for the superuser",
        )
        parser.add_argument(
            "--password",
            type=str,
            default="admin123",
            help="Password for the superuser",
        )

    def handle(self, *args, **options):
        username = options["username"]
        email = options["email"]
        password = options["password"]

        self.stdout.write("Creating Django superuser...")

        try:
            # Check if superuser already exists
            if User.objects.filter(username=username).exists():
                self.stdout.write(
                    self.style.WARNING(f'Superuser "{username}" already exists.')
                )
                return

            # Create superuser
            user = User.objects.create_superuser(
                username=username, email=email, password=password
            )

            self.stdout.write(
                self.style.SUCCESS(f'Successfully created superuser "{username}"')
            )
            self.stdout.write(f"Username: {username}")
            self.stdout.write(f"Email: {email}")
            self.stdout.write(f"Password: {password}")
            self.stdout.write("")
            self.stdout.write(
                "You can now access Django admin at: http://localhost:8000/admin/"
            )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error creating superuser: {str(e)}"))
