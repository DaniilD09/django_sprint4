from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.urls import reverse

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
    EditUserProfileForm,
)
from .models import Category, Post, User
from .mixins import (
    PostMixin,
    CommentEditMixin,
    OnlyAuthorMixin,
)


class PostCreateView(
    LoginRequiredMixin,
    PostMixin,
    CreateView
):
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse(
            'blog:profile', kwargs={'username': self.request.user.username}
        )


class PostDeleteView(
    LoginRequiredMixin,
    PostMixin,
    OnlyAuthorMixin,
    DeleteView
):
    pk_url_kwarg = 'post_id'

    def get_success_url(self):
        return reverse(
            'blog:index',
        )


class PostUpdateView(
    LoginRequiredMixin,
    PostMixin,
    OnlyAuthorMixin,
    UpdateView
):
    pk_url_kwarg = 'post_id'
    form_class = PostForm

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class CommentCreateView(
    LoginRequiredMixin,
    CommentEditMixin,
    CreateView
):
    pk_url_kwarg = 'post_id'
    form_class = CreateCommentForm

    def form_valid(self, form):
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        form.instance.author = self.request.user
        return super().form_valid(form)


class CommentDeleteView(
    LoginRequiredMixin,
    CommentEditMixin,
    OnlyAuthorMixin,
    DeleteView
):
    pass


class CommentUpdateView(
    LoginRequiredMixin,
    CommentEditMixin,
    OnlyAuthorMixin,
    UpdateView
):
    pass


class ProfileListView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    paginate_by = PAGINATED_BY

    def get_queryset(self):
        profile = get_object_or_404(
            User,
            username=self.kwargs.get('username')
        )
# просто перенсти скобочку?
        return profile.posts.all().annotate(
            comment_count=Count('comments')).order_by('-pub_date')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(
            User,
            username=self.kwargs.get('username')
        )
        return context


class CategoryListView(ListView):
    model = Post
    template_name = 'blog/category.html'
    context_object_name = 'post_list'
    paginate_by = PAGINATED_BY

    def get_queryset(self):
        category = get_object_or_404(
            Category,
            slug=self.kwargs.get('category_slug'), is_published=True
        )
        return category.posts(manager='published_posts').all()


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
            return (
                get_object_or_404(self.model.objects.select_related(
                    'location',
                    'author',
                    'category'),
                    pk=self.kwargs.get(self.pk_url_kwarg))
            )
        return get_object_or_404(
            Post.published_posts.annotate(
                comment_count=Count('comments')
            ).order_by('-pub_date')
        )


class IndexListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    paginate_by = PAGINATED_BY
    queryset = Post.published_posts.annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')


class UserProfileUpdateView(
    LoginRequiredMixin, UpdateView
):
    model = User
    form_class = EditUserProfileForm
    template_name = 'blog/user.html'

    def get_success_url(self):
        return reverse('blog:index')

    def get_object(self):
        return self.request.user
