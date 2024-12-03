from django.db import models
from django.utils import timezone


class PublishedRecordingsManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related(
            'category',
            'location',
            'author'
        ).filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        )
