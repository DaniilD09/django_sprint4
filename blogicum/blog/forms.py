from django import forms
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import Comment, Post

User = get_user_model()


class PostForm(forms.ModelForm):
    pub_date = forms.DateTimeField(
        initial=timezone.now,
        required=True,
        widget=forms.DateTimeInput(
            attrs={'type': 'datetime-local', },
            format='%Y-%m-%dT%H:%M',
        ),
    )

    class Meta:
        model = Post
        exclude = ('author', 'created_at')


class CreateCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)


class EditUserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
