from django.contrib.auth.mixins import LoginRequiredMixin
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
    CommentForm,
    PostForm,
    EditUserProfileForm,
    CustomUserCreationForm
)
from .models import Category, Comment, Post, User
from .mixins import PostMixin, CommentEditMixin
from .managers import filtered_post


class PostCreateView(PostMixin, LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse(
            'blog:profile',
            args=[self.request.user.username]
        )


class PostUpdateView(PostMixin, LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=self.kwargs[self.pk_url_kwarg])
        if self.request.user != post.author:
            return redirect('blog:post_detail',
                            post_id=self.kwargs[self.pk_url_kwarg])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:post_detail',
                       args=[self.kwargs[self.pk_url_kwarg]])


class PostDeleteView(PostMixin, LoginRequiredMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('blog:index')
    pk_url_kwarg = 'post_id'

    def delete(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=self.kwargs[self.pk_url_kwarg])
        if self.request.user != post.author:
            return redirect('blog:index')
        return super().delete(request, *args, **kwargs)


class UserCreateView(CreateView):
    template_name = 'registration/registration_form.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('users:login')


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = EditUserProfileForm
    template_name = 'blog/user.html'

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile', kwargs={'username': self.object.username}
        )

    def get_object(self):
        return self.request.user


class CommentCreateView(CommentEditMixin, LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        form.instance.author = self.request.user
        return super().form_valid(form)


class CommentUpdateView(CommentEditMixin, LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        comment = get_object_or_404(Comment, pk=self.kwargs[self.pk_url_kwarg])
        if self.request.user != comment.author:
            return redirect('blog:post_detail', post_id=self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)


class CommentDeleteView(CommentEditMixin, LoginRequiredMixin, DeleteView):
    model = Comment
    pk_url_kwarg = 'comment_id'

    def delete(self, request, *args, **kwargs):
        comment = get_object_or_404(Comment, pk=self.kwargs[self.pk_url_kwarg])
        if self.request.user != comment.author:
            return redirect('blog:post_detail', post_id=self.kwargs['post_id'])
        return super().delete(request, *args, **kwargs)


class ProfileListView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    paginate_by = PAGINATED_BY

    def get_queryset(self):
        username = get_object_or_404(User, username=self.kwargs['username'])
        posts = username.posts.all()
        if self.request.user != username:
            posts = filtered_post(posts)
        return posts

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(
            User, username=self.kwargs['username']
        )
        return context


class IndexListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    paginate_by = PAGINATED_BY

    queryset = filtered_post(Post.objects)


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

    def get_object(self, queryset=None):
        post = get_object_or_404(Post, pk=self.kwargs.get(self.pk_url_kwarg))
        if self.request.user == post.author:
            return post
        return get_object_or_404(
            filtered_post(Post.objects.all()),
            pk=self.kwargs.get(self.pk_url_kwarg)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.get_object().comments.prefetch_related('author').all()
        )
        return context
