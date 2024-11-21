from django.db import models
from django.db.models import Count
from django.utils import timezone


def filter_published_posts(posts):
    return posts.filter(
        is_published=True,
        pub_date__lte=timezone.now(),
        category__is_published=True
    ).annotate(
        comment_count=Count('comments')
    ).order_by(
        '-pub_date'
    ).select_related(
        'category', 'author', 'location'
    )


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
