import uuid

from django.db import models
from django.utils import timezone


class AbstractBase(models.Model):
    """
    Contains common fields required in each model.
    """
    id = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, primary_key=True,
        help_text="Unique identifier of an object")
    created = models.DateTimeField(
        db_index=True, default=timezone.now,
        help_text="Date and time an object was created")
    updated = models.DateTimeField(
        db_index=True, default=timezone.now,
        help_text="Date and time an object was updated")

    class Meta:
        abstract = True
        ordering = ("-updated", "-created",)
