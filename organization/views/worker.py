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

from organization.forms import WorkerForm
from organization.models import Worker


class WorkerListView(ListView):
    """Просмотр списка структурных подразделений"""

    model = Worker


class WorkerDetailView(DetailView):
    """Просмотр одной из структурных подразделений"""

    model = Worker


class WorkerCreateView(CreateView):
    """Создание структурных подразделений"""

    model = Worker
    form_class = WorkerForm

    def get_success_url(self):
        return reverse("worker:worker_detail", args=[self.object.pk])


class WorkerUpdateView(UpdateView):
    """Редактирование структурных подразделений"""

    model = Worker
    form_class = WorkerForm

    def get_success_url(self):
        return reverse("worker:worker_detail", args=[self.object.pk])


class WorkerDeleteView(DeleteView):
    """Удаление структурных подразделений"""

    model = Worker
    success_url = reverse_lazy("worker:worker_list")
