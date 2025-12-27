from django.apps import AppConfig


class PagesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "pages"

    def ready(self):
        from django.conf import settings

        if "sqlite3" in settings.DATABASES["default"]["ENGINE"]:
            from django.db import connection

            with connection.cursor() as cursor:
                cursor.execute("PRAGMA journal_mode=WAL;")
                cursor.execute("PRAGMA synchronous=NORMAL;")
