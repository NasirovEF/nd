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

from learning.forms import ProgramForm
from learning.models import Program


class ProgramListView(ListView):
    """Просмотр списка филиалов"""

    model = Program


class ProgramDetailView(DetailView):
    """Просмотр одного из филиалов"""

    model = Program


class ProgramCreateView(CreateView):
    """Создание филиалов"""

    model = Program
    form_class = ProgramForm

    def get_success_url(self):
        return reverse("organization:organization_list")


class ProgramUpdateView(UpdateView):
    """Редактирование филиалов"""

    model = Program
    form_class = ProgramForm

    def get_success_url(self):
        return reverse("organization:organization_list")


class ProgramDeleteView(DeleteView):
    """Удаление филиала"""

    model = Program
    success_url = reverse_lazy("organization:organization_list")
