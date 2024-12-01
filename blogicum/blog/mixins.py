from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth import login
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.urls import reverse

from .forms import CreateCommentForm
from .models import Post, Comment

User = get_user_model()


class PostMixin:
    model = Post
    template_name = 'blog/create.html'


class CommentEditMixin:
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'
    model = Comment
    form_class = CreateCommentForm

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class LoginMixin:
    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('blog:index')


class OnlyAuthorMixin(UserPassesTestMixin):
    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user

    def handle_no_permission(self):
        return redirect(
            'blog:post_detail', post_id=self.get_object().pk
        )


# Привет блогикум urls посмотри что то не совсем понял что да как
# Поправил не много
# Отправляю на проверку потому что дальше буду путаться надо новый старт
# смотри сверху сделал импорты по алфовиту
# cначала импорт делаем forms? потому что буква F по алфавиту стоит
# первее чем models? буква M? верно понимаю
