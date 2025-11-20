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

from organization.forms import PositionForm
from organization.models import Position


class PositionListView(ListView):
    """Просмотр списка профессий/должностей"""

    model = Position


class PositionDetailView(DetailView):
    """Просмотр одной профессии/должности"""

    model = Position


class PositionCreateView(CreateView):
    """Создание профессии/должности"""

    model = Position
    form_class = PositionForm

    def get_success_url(self):
        return reverse("organization:organization_list")


class PositionUpdateView(UpdateView):
    """Редактирование профессии/должности"""

    model = Position
    form_class = PositionForm

    def get_success_url(self):
        return reverse("organization:organization_list")


class PositionDeleteView(DeleteView):
    """Удаление профессии/должности"""
    model = Position
    success_url = reverse_lazy("organization:organization_list")
