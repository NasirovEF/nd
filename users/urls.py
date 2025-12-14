from django.urls import path
from users.apps import UsersConfig
from users.views import UserLoginView
from django.contrib.auth.views import LogoutView

app_name = UsersConfig.name

urlpatterns = [
    path("login/", UserLoginView.as_view(template_name="user/login.html"), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
