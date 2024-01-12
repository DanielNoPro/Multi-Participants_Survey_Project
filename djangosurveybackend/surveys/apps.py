from django.apps import AppConfig

from surveybackend import container


class SurveysConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'surveys'

    def ready(self):
        container.wire(modules=[".views"])
