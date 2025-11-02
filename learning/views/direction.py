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

from learning.forms import DirectionForm
from learning.models import Direction


class DirectionListView(ListView):
    """Просмотр списка филиалов"""

    model = Direction


class DirectionDetailView(DetailView):
    """Просмотр одного из филиалов"""

    model = Direction


class DirectionCreateView(CreateView):
    """Создание филиалов"""

    model = Direction
    form_class = DirectionForm

    def get_success_url(self):
        return reverse("organization:organization_list")


class DirectionUpdateView(UpdateView):
    """Редактирование филиалов"""

    model = Direction
    form_class = DirectionForm

    def get_success_url(self):
        return reverse("organization:organization_list")


class DirectionDeleteView(DeleteView):
    """Удаление филиала"""

    model = Direction
    success_url = reverse_lazy("organization:organization_list")
