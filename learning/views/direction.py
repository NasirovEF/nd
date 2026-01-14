from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
    View,
)
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from learning.forms import DirectionForm
from learning.models import Direction


class DirectionListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """Просмотр списка филиалов"""

    model = Direction
    permission_required = 'learning.view_direction'


class DirectionDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    """Просмотр одного из филиалов"""

    model = Direction
    permission_required = 'learning.view_direction'


class DirectionCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Создание филиалов"""

    model = Direction
    form_class = DirectionForm
    permission_required = 'learning.add_direction'

    def get_success_url(self):
        return reverse("organization:organization_list")


class DirectionUpdateView(LoginRequiredMixin, PermissionRequiredMixin,  UpdateView):
    """Редактирование филиалов"""

    model = Direction
    form_class = DirectionForm
    permission_required = 'learning.change_direction'

    def get_success_url(self):
        return reverse("organization:organization_list")


class DirectionDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Удаление направлений обучения"""

    model = Direction
    permission_required = 'learning.delete_direction'
    success_url = reverse_lazy("organization:organization_list")
