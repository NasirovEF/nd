from django.shortcuts import render
from django.contrib.auth.views import LoginView

from users.forms import UserLoginViewForm
from users.models import User


class UserLoginView(LoginView):
    model = User
    form_class = UserLoginViewForm
