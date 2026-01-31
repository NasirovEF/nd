from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from learning.models import Direction


class DirectionListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """Просмотр списка направлений обучения"""

    model = Direction
    permission_required = 'learning.view_direction'
    paginate_by = 15


