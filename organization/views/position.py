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
    """Просмотр списка ОСТов"""

    model = Position


class PositionDetailView(DetailView):
    """Просмотр одного из ОСТов"""

    model = Position


class PositionCreateView(CreateView):
    """Создание ОСТа"""

    model = Position
    form_class = PositionForm

    def get_success_url(self):
        return reverse("position:position_detail", args=[self.object.pk])


class PositionUpdateView(UpdateView):
    """Редактирование ОСТа"""

    model = Position
    form_class = PositionForm

    def get_success_url(self):
        return reverse("position:position_detail", args=[self.object.pk])


class PositionDeleteView(DeleteView):
    model = Position
    success_url = reverse_lazy("position:position_list")
