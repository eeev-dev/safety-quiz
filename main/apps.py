from django.apps import AppConfig
from django.db.models.signals import post_migrate


def create_settings_instance(sender, **kwargs):
    from .models import Settings
    Settings.objects.get_or_create(pk=1)


class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'

    def ready(self):
        post_migrate.connect(create_settings_instance, sender=self)
