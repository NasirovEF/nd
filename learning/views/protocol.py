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
from learning.models import Protocol, KnowledgeDate, ProtocolResult, Direction, Learner
from organization.models import Division, Worker


class ProtocolListView(ListView):
    """Просмотр списка протоколов"""

    model = Protocol

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        divisions = Division.objects.all()
        directions = Direction.objects.all()
        context["divisions"] = divisions
        context["directions"] = directions
        context['search_params'] = {
            'division': self.request.GET.get('division', ''),
            'direction': self.request.GET.get('direction', ''),
            'date_from': self.request.GET.get('date_from', ''),
            'date_to': self.request.GET.get('date_to', ''),
            'has_file': self.request.GET.get('has_file', ''),
            'has_not_file': self.request.GET.get('has_not_file', ''),
            'surname': self.request.GET.get('surname', ''),
            'name': self.request.GET.get('name', ''),
            'patronymic': self.request.GET.get('patronymic', ''),
        }
        return context

    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)

        division = self.request.GET.get("division")
        direction = self.request.GET.get("direction")
        date_from = self.request.GET.get("date_from")
        date_to = self.request.GET.get("date_to")
        has_file = self.request.GET.get("has_file")
        has_not_file = self.request.GET.get("has_not_file")
        surname = self.request.GET.get("surname")
        name = self.request.GET.get("name")
        patronymic = self.request.GET.get("patronymic")

        if division:
            queryset = queryset.filter(division__name__icontains=division)
        if direction:
            queryset = queryset.filter(direction__name__icontains=direction)
        if date_from:
            queryset = queryset.filter(prot_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(prot_date__lte=date_to)
        if has_file == "1" and has_not_file != "0":
            queryset = queryset.exclude(doc_scan='').filter(doc_scan__isnull=False)
        elif has_file != "1" and has_not_file == "0":
            queryset = queryset.filter(doc_scan='')
        elif has_file == "1" and has_not_file == "0":
            queryset = queryset.filter()
        if surname:
            worker = Worker.objects.filter(surname__icontains=surname)
            learner = Learner.objects.filter(worker__in=worker)
            queryset = queryset.filter(learner__in=learner)
        if name:
            worker = Worker.objects.filter(name__icontains=name)
            learner = Learner.objects.filter(worker__in=worker)
            queryset = queryset.filter(learner__in=learner)
        if patronymic:
            worker = Worker.objects.filter(patronymic__icontains=patronymic)
            learner = Learner.objects.filter(worker__in=worker)
            queryset = queryset.filter(learner__in=learner)

        return queryset


class ProtocolDetailView(DetailView):
    """Просмотр одного из протокола"""

    model = Protocol

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['results'] = ProtocolResult.objects.filter(
            protocol=self.object
        ).select_related('learner')
        return context


class ProtocolCreateView(CreateView):
    """Создание протокола"""

    model = Protocol
    form_class = ProtocolCreateForm

    def get_success_url(self):
        return reverse("learning:protocol_list")

    def form_valid(self, form):
        protocol = form.save()
        directions = protocol.direction.all()
        learners = protocol.learner.all()

        for learner in learners:
            ProtocolResult.objects.create(
                protocol=protocol,
                learner=learner,
                passed=True
            )

        for direction in directions:
            for learner in learners:
                knowledge_date = KnowledgeDate.objects.create_or_update_active(kn_date=protocol.prot_date, protocol=protocol, direction=direction, learner=learner)
                knowledge_date.save()

        return super().form_valid(form)


class ProtocolUpdateView(UpdateView):
    """Редактирование протокола"""

    model = Protocol
    form_class = ProtocolUpdateForm

    def get_success_url(self):
        return reverse("learning:protocol_list")

    def form_valid(self, form):
        protocol = form.save()
        self.object.protocol_result.all().delete()
        self.object.knowledge_date.all().delete()

        for learner in protocol.learner.all():
            result = ProtocolResult.objects.create(
                protocol=protocol,
                learner=learner,
                passed=True
            )
            result.save()

        for direction in protocol.direction.all():
            for learner in protocol.learner.all():
                knowledge_date = KnowledgeDate.objects.create_or_update_active(kn_date=protocol.prot_date, protocol=protocol,
                                                              direction=direction, learner=learner)
                knowledge_date.save()

        return super().form_valid(form)


class ProtocolDeleteView(DeleteView):
    """Удаление филиала"""

    model = Protocol
    success_url = reverse_lazy("learning:protocol_list")
