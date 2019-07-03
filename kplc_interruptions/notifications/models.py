from django.contrib.postgres.fields import ArrayField
from django.db import models

from kplc_interruptions.common.models import AbstractBase
from kplc_interruptions.interruptions.models import InterruptionPdfText


class NotificationAccount(AbstractBase):
    """
    Accounts to receive notifications if their areas are found in any of the
    scraped PDF files.
    """
    email = models.EmailField(
        unique=True, help_text="Email of the person to be notified")
    areas = ArrayField(
        models.CharField(max_length=255), blank=True,
        help_text="Areas to be searched for in the extracted PDFs")
    is_active = models.BooleanField()

    def __str__(self):
        return "{email}: {areas}".format(self.email, self.areas)


class NotificationLog(AbstractBase):
    """
    Logs success/error messages for notifications sent out to accounts.
    """
    LOG_STATUS_CHOICES = (
        ("PENDING", "Pending"),
        ("SUCCESS", "Success"),
        ("FAILURE", "Failure"),
    )
    account = models.ForeignKey(
        NotificationAccount, related_name="account_logs",
        on_delete=models.PROTECT)
    status = models.CharField(max_length=7, choices=LOG_STATUS_CHOICES)
    message = models.TextField(blank=True)


class NotificationPDFQueue(AbstractBase):
    """
    Queue of PDFs to be processed and sent out to accounts.
    """
    pdf_text = models.OneToOneField(
        InterruptionPdfText, related_name="pdf_queue",
        on_delete=models.PROTECT)
    is_processed = models.BooleanField(default=False)
    processed_on = models.DateTimeField()
