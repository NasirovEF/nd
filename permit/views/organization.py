from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView, View)

from permit.forms.organization import OrganizationForm
from permit.models import Organization


class OrganizationListView(ListView):
    """Просмотр списка ОСТов"""
    model = Organization


class OrganizationDetailView(DetailView):
    """Просмотр одного из ОСТов"""
    model = Organization


class OrganizationCreateView(CreateView):
    """Создание ОСТа"""
    model = Organization
    form_class = OrganizationForm

    def get_success_url(self):
        return reverse("permit:organization_detail", args=[self.object.pk])


class OrganizationUpdateView(UpdateView):
    """Редактирование ОСТа"""
    model = Organization
    form_class = OrganizationForm

    def get_success_url(self):
        return reverse("permit:organization_detail", args=[self.object.pk])


class OrganizationDeleteView(DeleteView):
    model = Organization
    success_url = reverse_lazy("permit:organization_list")



