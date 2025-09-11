from django.apps import AppConfig


class CoursewareConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'courseware'

    def ready(self):
        from . import signals