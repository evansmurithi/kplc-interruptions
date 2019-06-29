from django.apps import AppConfig
from django.conf import settings
from elasticsearch_dsl import connections


class InterruptionsConfig(AppConfig):
    name = 'kplc_interruptions.interruptions'

    def ready(self):
        connections.create_connection(settings.ES_SETTINGS["ALIAS"], hosts=[{
            "host": settings.ES_SETTINGS["HOST"],
            "port": settings.ES_SETTINGS["PORT"]
        }])
