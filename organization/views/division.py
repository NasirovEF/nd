from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView, View)

from organization.forms import DivisionForm
from organization.models import Division


class DivisionListView(ListView):
    """Просмотр списка структурных подразделений"""
    model = Division


class DivisionDetailView(DetailView):
    """Просмотр одной из структурных подразделений"""
    model = Division


class DivisionCreateView(CreateView):
    """Создание структурных подразделений"""
    model = Division
    form_class = DivisionForm

    def get_success_url(self):
        return reverse("division:division_detail", args=[self.object.pk])


class BranchUpdateView(UpdateView):
    """Редактирование структурных подразделений"""
    model = Division
    form_class = DivisionForm

    def get_success_url(self):
        return reverse("division:division_detail", args=[self.object.pk])


class DivisionDeleteView(DeleteView):
    """Удаление структурных подразделений"""
    model = Division
    success_url = reverse_lazy("division:division_list")



