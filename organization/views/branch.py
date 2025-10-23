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
from organization.models import Branch


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

    def get_success_url(self):
        return reverse("branch:branch_detail", args=[self.object.pk])


class BranchUpdateView(UpdateView):
    """Редактирование филиалов"""

    model = Branch
    form_class = BranchForm

    def get_success_url(self):
        return reverse("branch:branch_detail", args=[self.object.pk])


class BranchDeleteView(DeleteView):
    """Удаление филиала"""

    model = Branch
    success_url = reverse_lazy("branch:branch_list")
