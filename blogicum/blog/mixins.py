from django.urls import reverse

from .models import Post, Comment


class PostMixin:
    model = Post
    template_name = 'blog/create.html'


class CommentMixin:
    model = Comment
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            args=[self.kwargs['post_id']]
        )


# Иногда тут буду писать свои идеи может подкоректируешь заодно)
# Привет по прошлым всем правкам, я думаю ты попросишь сделать отдельный файл для Миксин
# в константу добавил значение для пагинатора) сразу стараюсь делать красиво),
# избавился от core, модель из нее добавил в blog/models.py
# изменил urls.py в pages
