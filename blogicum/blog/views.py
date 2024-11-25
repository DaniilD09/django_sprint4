from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.contrib.auth import login
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from blogicum.constants import PAGINATED_BY

from .forms import (
    CreateCommentForm,
    PostForm,
    CustomUserCreationForm,
    EditUserProfileForm,
)
from .models import Category, Post, Comment, User
from .mixins import PostMixin, CommentEditMixin
from .managers import filtered_post


class PostCreateView(LoginRequiredMixin, PostMixin, CreateView):

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse(
            'blog:profile', kwargs={'username': self.request.user.username}
        )


class PostDeleteView(UserPassesTestMixin, PostMixin,
                     DeleteView):
    pk_url_kwarg = 'post_id'

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user

    def delete(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=self.kwargs[self.pk_url_kwarg])
        if self.request.user != post.author:
            return redirect('blog:index')
        return super().delete(request, *args, **kwargs)


class PostUpdateView(LoginRequiredMixin, PostMixin, UpdateView):
    pk_url_kwarg = 'post_id'
    form_class = PostForm

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


class CommentCreateView(LoginRequiredMixin, CommentEditMixin, CreateView):
    pk_url_kwarg = 'post_id'
    form_class = CreateCommentForm

    def form_valid(self, form):
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        form.instance.author = self.request.user
        return super().form_valid(form)


class CommentDeleteView(LoginRequiredMixin, CommentEditMixin, DeleteView):

    def dispatch(self, request, *args, **kwargs):
        comment = get_object_or_404(
            Comment,
            pk=kwargs['comment_id'],
        )
        if comment.author != request.user:
            return redirect('blog:post_detail', id=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)


class CommentUpdateView(LoginRequiredMixin, CommentEditMixin, UpdateView):
    form_class = CreateCommentForm

    def dispatch(self, request, *args, **kwargs):
        comment = get_object_or_404(Comment, pk=kwargs['comment_id'],)
        if comment.author != request.user:
            return redirect('blog:post_detail', id=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)


class ProfileListView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    paginate_by = PAGINATED_BY

    def get_queryset(self):
        profile = get_object_or_404(
            User, username=self.kwargs.get('username'))
        return profile.users.all().annotate(
            comment_count=Count('comments')).order_by('-pub_date',)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(
            User, username=self.kwargs.get('username'))
        return context


class CategoryListView(ListView):
    model = Post
    template_name = 'blog/category.html'
    context_object_name = 'post_list'
    paginate_by = PAGINATED_BY

    def get_queryset(self):
        category_slug = self.kwargs['category_slug']
        category = get_object_or_404(Category, slug=category_slug,
                                     is_published=True)
        posts = filtered_post(category.posts.all())
        return posts


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CreateCommentForm()
        context['comments'] = self.object.comments.select_related('author')
        return context

    def get_object(self, queryset=None):
        post = super().get_object(queryset=queryset)
        if post.author == self.request.user:
            return (get_object_or_404(
                self.model.objects
                .select_related(
                    'location',
                    'author',
                    'category'
                ),
                pk=self.kwargs.get(self.pk_url_kwarg)))
        return (get_object_or_404(
            filtered_post(self.model.objects),
                pk=self.kwargs.get(self.pk_url_kwarg)))


class IndexListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    paginate_by = PAGINATED_BY

    queryset = filtered_post(Post.objects)


class UserCreateView(CreateView):
    template_name = 'registration/registration_form.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('blog:index')


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = EditUserProfileForm
    template_name = 'blog/user.html'

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('blog:index')

    def get_object(self):
        return self.request.user
