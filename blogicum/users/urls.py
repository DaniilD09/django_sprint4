from django.urls import path, include

from . import views

app_name = 'users'

urlpatterns = [
    path(
        'auth/registration/',
        views.UserCreateView.as_view(),
        name='registration',
    ),
    path(
        'auth/',
        include('django.contrib.auth.urls')
    ),
]
