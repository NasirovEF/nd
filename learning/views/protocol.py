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

from learning.forms import ProtocolForm
from learning.models import Protocol, KnowledgeDate


class ProtocolListView(ListView):
    """Просмотр списка филиалов"""

    model = Protocol


class ProtocolDetailView(DetailView):
    """Просмотр одного из филиалов"""

    model = Protocol


class ProtocolCreateView(CreateView):
    """Создание филиалов"""

    model = Protocol
    form_class = ProtocolForm

    def get_success_url(self):
        return reverse("learning:protocol_list")

    def form_valid(self, form):
        protocol = form.save()
        for direction in protocol.direction.all():
            for learner in protocol.learner.all():
                knowledge_date = KnowledgeDate.objects.create(date=protocol.date, protocol=protocol, direction=direction, learner=learner)
                knowledge_date.save()

        return super().form_valid(form)


class ProtocolUpdateView(UpdateView):
    """Редактирование филиалов"""

    model = Protocol
    form_class = ProtocolForm

    def get_success_url(self):
        return reverse("learning:protocol_list")


class ProtocolDeleteView(DeleteView):
    """Удаление филиала"""

    model = Protocol
    success_url = reverse_lazy("learning:protocol_list")
