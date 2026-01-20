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
from organization.forms import DivisionForm
from organization.models import Division, Organization, Branch


class DivisionListView(ListView):
    """Просмотр списка структурных подразделений"""

    model = Division


class DivisionDetailView(DetailView):
    """Просмотр одной из структурных подразделений"""

    model = Division


class DivisionCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Создание структурных подразделений"""

    model = Division
    form_class = DivisionForm
    permission_required = 'organization.add_division'

    def get_success_url(self):
        return reverse("organization:organization_list")

    def form_valid(self, form):
        division = form.save()
        branch = self.request.GET["branch"]
        division.branch = Branch.objects.get(pk=branch)
        form.save()

        return super().form_valid(form)


class DivisionUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Редактирование структурных подразделений"""

    model = Division
    form_class = DivisionForm
    permission_required = 'organization.change_division'

    def get_success_url(self):
        return reverse("organization:organization_list")


class DivisionDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Удаление структурных подразделений"""

    model = Division
    permission_required = 'organization.delete_division'
    success_url = reverse_lazy("organization:organization_list")
