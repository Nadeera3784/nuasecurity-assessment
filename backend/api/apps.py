from django.apps import AppConfig
from django.conf import settings
import os


class ApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "api"

    def ready(self):
        from neomodel import config

        config.DATABASE_URL = getattr(
            settings,
            "NEOMODEL_NEO4J_BOLT_URL",
            os.getenv("NEO4J_BOLT_URL", "bolt://neo4j:password@localhost:7687"),
        )
