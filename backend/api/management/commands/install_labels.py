"""
Management command to install Neo4j labels/constraints.
"""

from django.core.management.base import BaseCommand
from neomodel import install_all_labels


class Command(BaseCommand):
    help = "Install Neo4j labels and constraints"

    def handle(self, *args, **options):
        self.stdout.write("Installing Neo4j labels and constraints...")
        try:
            install_all_labels()
            self.stdout.write(
                self.style.SUCCESS(
                    "Successfully installed Neo4j labels and constraints"
                )
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error installing labels: {str(e)}"))
