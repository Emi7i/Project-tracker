from django.apps import AppConfig


class ProjectsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'projects'

    def ready(self):
        from django.db.models.signals import post_migrate
        from .signals import create_default_profile

        post_migrate.connect(create_default_profile, sender=self)
