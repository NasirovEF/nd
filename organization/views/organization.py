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

from organization.forms import OrganizationForm
from organization.models import Organization, Branch


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
        return reverse("organization:organization_list")


class OrganizationUpdateView(UpdateView):
    """Редактирование ОСТа"""

    model = Organization
    form_class = OrganizationForm

    def get_success_url(self):
        return reverse("organization:organization_list")


class OrganizationDeleteView(DeleteView):
    model = Organization
    success_url = reverse_lazy("organization:organization_list")
