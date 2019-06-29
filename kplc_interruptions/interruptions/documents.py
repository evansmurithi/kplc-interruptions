from django.conf import settings
from elasticsearch_dsl import Document, Text, analyzer


pdf_text_analyzer = analyzer(
    'pdf_text_analyzer', tokenizer="standard",
    filter=["lowercase", "stop", "snowball"]
)


class InterruptionPdfTextDoc(Document):
    pdf_text = Text(analyzer=pdf_text_analyzer)

    class Index:
        name = "kplc_interruptions"
        using = settings.ES_SETTINGS["ALIAS"]
