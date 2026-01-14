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
from organization.forms import PositionForm
from organization.models import Position


class PositionListView(ListView):
    """Просмотр списка профессий/должностей"""

    model = Position


class PositionDetailView(DetailView):
    """Просмотр одной профессии/должности"""

    model = Position


class PositionCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Создание профессии/должности"""

    model = Position
    form_class = PositionForm
    permission_required = 'organization.add_position'

    def get_success_url(self):
        return reverse("organization:organization_list")


class PositionUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Редактирование профессии/должности"""

    model = Position
    form_class = PositionForm
    permission_required = 'organization.change_position'

    def get_success_url(self):
        return reverse("organization:organization_list")


class PositionDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Удаление профессии/должности"""

    model = Position
    permission_required = 'organization.delete_position'
    success_url = reverse_lazy("organization:organization_list")
