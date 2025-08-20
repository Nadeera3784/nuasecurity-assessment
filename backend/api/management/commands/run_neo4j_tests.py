"""
Management command to run tests with Neo4j configuration.
"""

import os
from django.core.management.base import BaseCommand
from django.test.utils import get_runner
from django.conf import settings
from neomodel import config


class Command(BaseCommand):
    help = "Run API tests with proper Neo4j configuration"

    def add_arguments(self, parser):
        parser.add_argument(
            "--test-case",
            type=str,
            help="Specific test case to run (e.g., api.tests.AuthenticationTestCase)",
        )
        parser.add_argument(
            "--keepdb",
            action="store_true",
            help="Keep test database after tests",
        )

    def handle(self, *args, **options):
        """Run the tests with Neo4j configuration"""

        # Configure Neo4j
        neo4j_url = os.getenv("NEO4J_TEST_URL", "bolt://neo4j:password@localhost:7687")
        config.DATABASE_URL = neo4j_url

        self.stdout.write("🧪 Running Grocery Management System API Tests with Neo4j")
        self.stdout.write("=" * 60)
        self.stdout.write(f"Neo4j URL: {neo4j_url}")
        self.stdout.write("=" * 60)

        # Get test runner
        TestRunner = get_runner(settings)
        test_runner = TestRunner(
            verbosity=options.get("verbosity", 2), keepdb=options["keepdb"]
        )

        # Determine what to test
        if options["test_case"]:
            test_labels = [options["test_case"]]
            self.stdout.write(f"Running specific test: {options['test_case']}")
        else:
            test_labels = ["api.tests"]
            self.stdout.write("Running all API tests")

        # Run tests
        failures = test_runner.run_tests(test_labels)

        if failures:
            self.stdout.write(self.style.ERROR(f"\n❌ {failures} test(s) failed"))
            return failures
        else:
            self.stdout.write(self.style.SUCCESS("\n✅ All tests passed!"))
