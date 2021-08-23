from django.apps import AppConfig
from django.db import connection


class CorporationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'corporations'

    def ready(self):
        if 'django_q_schedule' in connection.introspection.table_names():
            from .tasks import initialize_tasks
            initialize_tasks()
