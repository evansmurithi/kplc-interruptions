from django.contrib.postgres.fields import ArrayField
from django.db import models

from kplc_interruptions.common.models import AbstractBase


class Notification(AbstractBase):
    email = models.EmailField(
        unique=True, help_text="Email of the person to be notified")
    areas = ArrayField(
        models.CharField(max_length=255), blank=True,
        help_text="Areas to be searched for in the extracted PDFs")
    is_active = models.BooleanField()

    def __str__(self):
        return "{email}: {areas}".format(self.email, self.areas)
