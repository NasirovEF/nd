from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView, View)

from organization.forms import DistrictForm
from organization.models import District


class DistrictListView(ListView):
    """Просмотр списка участков"""
    model = District


class DistrictDetailView(DetailView):
    """Просмотр одной из участков"""
    model = District


class DistrictCreateView(CreateView):
    """Создание участков"""
    model = District
    form_class = DistrictForm

    def get_success_url(self):
        return reverse("district:district_detail", args=[self.object.pk])


class BranchUpdateView(UpdateView):
    """Редактирование участков"""
    model = District
    form_class = DistrictForm

    def get_success_url(self):
        return reverse("district:district_detail", args=[self.object.pk])


class DistrictDeleteView(DeleteView):
    """Удаление участков"""
    model = District
    success_url = reverse_lazy("district:district_list")



