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
from organization.forms import BranchForm
from organization.models import Branch, Organization


class BranchListView(ListView):
    """Просмотр списка филиалов"""

    model = Branch


class BranchDetailView(DetailView):
    """Просмотр одного из филиалов"""

    model = Branch


class BranchCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Создание филиалов"""

    model = Branch
    form_class = BranchForm
    permission_required = 'organization.add_branch'

    def form_valid(self, form):
        branch = form.save()
        organization = self.request.GET["organization"]
        branch.organization = Organization.objects.get(pk=organization)
        form.save()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse("organization:organization_list")


class BranchUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Редактирование филиалов"""

    model = Branch
    form_class = BranchForm
    permission_required = 'organization.change_branch'

    def get_success_url(self):
        return reverse("organization:branch_detail", args=[self.object.pk])


class BranchDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Удаление филиала"""

    model = Branch
    permission_required = 'organization.delete_branch'
    success_url = reverse_lazy("organization:organization_list")
