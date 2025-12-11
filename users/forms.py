from organization.forms import StileFormMixin
from users.models import User
from  django.contrib.auth.forms import AuthenticationForm


class UserLoginViewForm(StileFormMixin, AuthenticationForm):
    model = User
    fields = ("username", "service_number", "password")