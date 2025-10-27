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

    # def get_queryset(self, *args, **kwargs):
    #     queriset = super().get_queryset(*args, **kwargs)
    #     queriset = queriset.filter(name_ost=self.pk)
    #     return queriset


class BranchDetailView(DetailView):
    """Просмотр одного из филиалов"""

    model = Branch


class BranchCreateView(CreateView):
    """Создание филиалов"""

    model = Branch
    form_class = BranchForm

    def form_valid(self, form):
        branch = form.save()
        name_ost = self.request.GET["name_ost"]
        branch.name_ost = Organization.objects.get(pk=name_ost)
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
