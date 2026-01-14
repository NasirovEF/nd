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
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from organization.forms import OrganizationForm
from organization.models import Organization, Branch


class OrganizationListView(ListView):
    """Просмотр списка ОСТов"""

    model = Organization

    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)
        queryset = queryset.filter(is_main=True)
        return queryset


class OrganizationDetailView(DetailView):
    """Просмотр одного из ОСТов"""

    model = Organization


class OrganizationCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Создание ОСТа"""

    model = Organization
    form_class = OrganizationForm
    permission_required = 'organization.add_organization'

    def get_success_url(self):
        return reverse("organization:organization_list")


class OrganizationUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Редактирование ОСТа"""

    model = Organization
    form_class = OrganizationForm
    permission_required = 'organization.change_organization'

    def get_success_url(self):
        return reverse("organization:organization_list")


class OrganizationDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Organization
    permission_required = 'organization.delete_organization'
    success_url = reverse_lazy("organization:organization_list")
