from django.urls import reverse

from .models import Comment, Post
from .forms import CommentForm, PostForm


class PostMixin:
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'


class CommentEditMixin:
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.kwargs['post_id']})

# Привет иногда тут буду писать свои идеи может подкоректируешь заодно
# 1. по прошлым всем правкам, я думаю ты попросишь сделать отдельный файл для
# Миксин
# 2. в константу добавил значение для пагинатора сразу стараюсь делать красиво,
# 3. избавился от core, модель из нее добавил в blog/models.py
# 4. изменил urls.py в pages
# 5. пытался сделать отдельное приложение users не смог пройти автотесты и не
# смог нормально поменять шаблоны, поэтому все в куче
# 6. скажу честно кое где списал кое где ребята помогали кое где сам
# 7. очень надеюсь что направишь и подскажешь что можно сделать хорошо очень
# хочу сделать красиво и правильно
