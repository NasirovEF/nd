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

from learning.forms import ProtocolCreateForm, ProtocolUpdateForm
from learning.models import Protocol, KnowledgeDate, ProtocolResult


class ProtocolListView(ListView):
    """Просмотр списка филиалов"""

    model = Protocol


class ProtocolDetailView(DetailView):
    """Просмотр одного из филиалов"""

    model = Protocol

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['results'] = ProtocolResult.objects.filter(
            protocol=self.object
        ).select_related('learner')
        return context


class ProtocolCreateView(CreateView):
    """Создание филиалов"""

    model = Protocol
    form_class = ProtocolCreateForm

    def get_success_url(self):
        return reverse("learning:protocol_list")

    def form_valid(self, form):
        protocol = form.save()
        for direction in protocol.direction.all():
            for learner in protocol.learner.all():
                knowledge_date = KnowledgeDate.objects.create(kn_date=protocol.prot_date, protocol=protocol, direction=direction, learner=learner)
                knowledge_date.save()

        for learner in protocol.learner.all():
            ProtocolResult.objects.create(
                protocol=protocol,
                learner=learner,
                passed=True
            )
        return super().form_valid(form)


class ProtocolUpdateView(UpdateView):
    """Редактирование филиалов"""

    model = Protocol
    form_class = ProtocolUpdateForm

    def get_success_url(self):
        return reverse("learning:protocol_list")

    def form_valid(self, form):
        protocol = form.save()
        self.object.protocol_result.all().delete()
        self.object.knowledge_date.all().delete()
        for direction in protocol.direction.all():
            for learner in protocol.learner.all():
                knowledge_date = KnowledgeDate.objects.create(date=protocol.date, protocol=protocol,
                                                              direction=direction, learner=learner)
                knowledge_date.create_next_date
                knowledge_date.save()

        for learner in protocol.learner.all():
            result = ProtocolResult.objects.create(
                protocol=protocol,
                learner=learner,
                passed=True
            )
            result.save()
        return super().form_valid(form)


class ProtocolDeleteView(DeleteView):
    """Удаление филиала"""

    model = Protocol
    success_url = reverse_lazy("learning:protocol_list")
