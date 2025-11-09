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
        return reverse("organization:district_detail", args=[self.object.district.pk])


class ProgramUpdateView(UpdateView):
    """Редактирование филиалов"""

    model = Program
    form_class = ProgramForm

    def get_success_url(self):
        return reverse("organization:district_detail", args=[self.object.district.pk])


class ProgramDeleteView(DeleteView):
    """Удаление филиала"""

    model = Program

    def get_success_url(self):
        return reverse("organization:district_detail", args=[self.request.GET["district"]])
