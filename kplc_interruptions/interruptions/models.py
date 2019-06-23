import os

from django.db import models

from kplc_interruptions.common.models import AbstractBase


class Interruption(AbstractBase):
    """
    Store interruption titles and links scraped from KPLC's power interruption
    website.
    """
    title = models.CharField(
        max_length=255, help_text="Title of the interruption link")
    link = models.URLField(
        max_length=255,
        help_text="URL to the PDF file(s) containing the interruptions")

    class Meta(AbstractBase.Meta):
        unique_together = ("title", "link")

    def __str__(self):
        return "{title} ({link})".format(title=self.title, link=self.link)


def interruption_upload_path(instance, filename):
    """
    Directory to upload interruption PDF files.
    """
    return "interruptions/{interruption_id}/{filename}".format(
        instance.interruption.id, filename)


class InterruptionPdf(AbstractBase):
    """
    Store KPLC power interruption PDF files and other details.
    """
    interruption = models.ForeignKey(
        Interruption, related_name="interruption_pdfs",
        on_delete=models.PROTECT)
    pdf_file = models.FileField(
        upload_to=interruption_upload_path,
        help_text="PDF downloaded from KPLC's website")
    pdf_name = models.CharField(
        max_length=255, help_text="Name displayed of the PDF")
    pdf_link = models.URLField(
        max_length=255, help_text="URL to download the PDF")

    class Meta(AbstractBase.Meta):
        unique_together = ("interruption", "pdf_link")

    def __str__(self):
        return "{filename} ({link})".format(
            filename=self.pdf_filename, link=self.pdf_link)

    @property
    def pdf_filename(self):
        return os.path.basename(self.pdf_file.name)
