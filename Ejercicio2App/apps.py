from django.apps import AppConfig


class Ejercicio2AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Ejercicio2App'

    def ready(self):
        import Ejercicio2App.signals  # noqa: F401