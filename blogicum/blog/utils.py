from django.db.models import Count
from django.utils import timezone


def post_query(posts):
    return posts.filter(
        is_published=True,
        pub_date__lte=timezone.now(),
        category__is_published=True
    ).annotate(
        comment_count=Count('comments')
    ).order_by(
        '-pub_date'
    )
