from django.contrib.auth.views import LoginView
from django.urls import reverse
from users.forms import UserLoginViewForm
from users.models import User


class UserLoginView(LoginView):
    model = User
    form_class = UserLoginViewForm

    def get_success_url(self):
        user = self.request.user
        if hasattr(user, 'worker') and user.worker is not None:
            return reverse(
                'organization:worker_detail',
                args=[user.worker.pk]
            )
        else:
            return reverse('organization:organization_list')
