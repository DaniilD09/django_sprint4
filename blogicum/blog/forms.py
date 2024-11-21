from django import forms
from django.utils import timezone

from .models import Post, Comment, User


class CreatePostForm(forms.ModelForm):
    pub_date = forms.DateTimeField(
        label='Дата и время',
        initial=timezone.now,
        required=True,
        widget=forms.DateTimeInput(
            attrs={
                'type': 'datetime-local',
                'format': '%Y-%m-%dT%H:%M',
            },),
    )

    class Meta:
        model = Post
        exclude = ('author', 'created_at',)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)


class EditUserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
