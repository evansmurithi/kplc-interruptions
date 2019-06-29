from django.conf import settings
from django.core.management.base import BaseCommand
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from elasticsearch_dsl import Index

from kplc_interruptions.interruptions.models import InterruptionPdfText
from kplc_interruptions.interruptions.documents import InterruptionPdfTextDoc


class Command(BaseCommand):

    def handle(self, *args, **options):
        index = "kplc_interruptions"
        es = Elasticsearch([{
            'host': settings.ES_SETTINGS['HOST'],
            'port': settings.ES_SETTINGS['PORT']
        }], index=index)
        kplc_index = Index(index, using=settings.ES_SETTINGS['ALIAS'])
        kplc_index.document(InterruptionPdfTextDoc)
        if kplc_index.exists():
            kplc_index.delete()
            # TODO: Use logger
            print('Deleted kplc interruptions index.')
        InterruptionPdfTextDoc.init()
        result = bulk(client=es, actions=(
            pdf.index() for pdf in InterruptionPdfText.objects.all().iterator()))
        # TODO: Use logger
        print('Indexed kplc interruptions.')
        print(result)
