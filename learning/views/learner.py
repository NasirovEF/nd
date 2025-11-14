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

from learning.forms import LearnerForm
from learning.models import Learner, Direction


class LearnerListView(ListView):
    """Просмотр списка филиалов"""

    model = Learner

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        directions = Direction.objects.all()
        context["directions"] = directions
        return context


class LearnerDetailView(DetailView):
    """Просмотр одного из филиалов"""

    model = Learner


class LearnerCreateView(CreateView):
    """Создание филиалов"""

    model = Learner
    form_class = LearnerForm

    def get_success_url(self):
        return reverse("organization:worker_detail", args=[self.object.worker.pk])


class LearnerUpdateView(UpdateView):
    """Редактирование филиалов"""

    model = Learner
    form_class = LearnerForm

    def get_success_url(self):
        return reverse("organization:worker_detail", args=[self.object.worker.pk])


class LearnerDeleteView(DeleteView):
    """Удаление филиала"""

    model = Learner
    success_url = reverse_lazy("organization:organization_list")
