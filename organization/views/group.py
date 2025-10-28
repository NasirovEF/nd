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

from organization.forms import GroupForm
from organization.models import Group, District


class GroupListView(ListView):
    """Просмотр списка групп"""

    model = Group


class GroupDetailView(DetailView):
    """Просмотр одной из групп"""

    model = Group


class GroupCreateView(CreateView):
    """Создание групп"""

    model = Group
    form_class = GroupForm

    def get_success_url(self):
        return reverse("organization:district_detail", args=[self.object.district.pk])

    def form_valid(self, form):
        group = form.save()
        district = self.request.GET["district"]
        group.district = District.objects.get(pk=district)
        form.save()

        return super().form_valid(form)


class GroupUpdateView(UpdateView):
    """Редактирование групп"""

    model = Group
    form_class = GroupForm

    def get_success_url(self):
        return reverse("organization:district_detail", args=[self.object.district.pk])


class GroupDeleteView(DeleteView):
    """Удаление групп"""

    model = Group
    success_url = reverse_lazy("organization:organization_list")
