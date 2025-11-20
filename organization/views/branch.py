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

from organization.forms import BranchForm
from organization.models import Branch, Organization


class BranchListView(ListView):
    """Просмотр списка филиалов"""

    model = Branch


class BranchDetailView(DetailView):
    """Просмотр одного из филиалов"""

    model = Branch


class BranchCreateView(CreateView):
    """Создание филиалов"""

    model = Branch
    form_class = BranchForm

    def form_valid(self, form):
        branch = form.save()
        organization = self.request.GET["organization"]
        branch.organization = Organization.objects.get(pk=organization)
        form.save()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse("organization:organization_list")


class BranchUpdateView(UpdateView):
    """Редактирование филиалов"""

    model = Branch
    form_class = BranchForm

    def get_success_url(self):
        return reverse("organization:branch_detail", args=[self.object.pk])


class BranchDeleteView(DeleteView):
    """Удаление филиала"""

    model = Branch
    success_url = reverse_lazy("organization:organization_list")
