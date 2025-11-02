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

from learning.forms import ProtocolForm
from learning.models import Protocol


class ProtocolListView(ListView):
    """Просмотр списка филиалов"""

    model = Protocol


class ProtocolDetailView(DetailView):
    """Просмотр одного из филиалов"""

    model = Protocol


class ProtocolCreateView(CreateView):
    """Создание филиалов"""

    model = Protocol
    form_class = ProtocolForm

    def get_success_url(self):
        return reverse("organization:organization_list")


class ProtocolUpdateView(UpdateView):
    """Редактирование филиалов"""

    model = Protocol
    form_class = ProtocolForm

    def get_success_url(self):
        return reverse("organization:organization_list")


class ProtocolDeleteView(DeleteView):
    """Удаление филиала"""

    model = Protocol
    success_url = reverse_lazy("organization:organization_list")
