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
from organization.models import Group


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
        return reverse("group:group_detail", args=[self.object.pk])


class GroupUpdateView(UpdateView):
    """Редактирование групп"""

    model = Group
    form_class = GroupForm

    def get_success_url(self):
        return reverse("group:group_detail", args=[self.object.pk])


class GroupDeleteView(DeleteView):
    """Удаление групп"""

    model = Group
    success_url = reverse_lazy("group:group_list")
