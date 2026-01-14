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
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.forms import inlineformset_factory
from learning.forms import LearnerForm
from learning.models import Learner, Direction, KnowledgeDate
from organization.models import Worker, Division


class LearnerListView(ListView):
    """Просмотр графика проверки знаний"""

    model = Learner


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
        surname = self.request.GET.get("surname")
        name = self.request.GET.get("name")
        patronymic = self.request.GET.get("patronymic")

        if division:
            queryset = queryset.filter(division__name__icontains=division)
        if direction:
            queryset = queryset.filter(direction__name__icontains=direction)
        if date_from:
            valid_learner_ids = KnowledgeDate.objects.filter(
                next_date__gte=date_from,
                is_active=True
            ).values_list('learner_id', flat=True)
            queryset = queryset.filter(id__in=valid_learner_ids)
        if date_to:
            valid_learner_ids = KnowledgeDate.objects.filter(
                next_date__lte=date_to,
                is_active=True
            ).values_list('learner_id', flat=True)
            queryset = queryset.filter(id__in=valid_learner_ids)
        if surname:
            worker = Worker.objects.filter(surname__icontains=surname)
            queryset = queryset.filter(worker__in=worker)
        if name:
            worker = Worker.objects.filter(name__icontains=name)
            queryset = queryset.filter(worker__in=worker)
        if patronymic:
            worker = Worker.objects.filter(patronymic__icontains=patronymic)
            queryset = queryset.filter(worker__in=worker)

        return queryset


class LearnerDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    """Просмотр одного из обучаемых"""

    model = Learner
    permission_required = 'learning.view_learner'


class LearnerCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Создание обучаемого"""

    model = Learner
    form_class = LearnerForm
    permission_required = 'learning.add_learner'

    def get_success_url(self):
        return reverse("organization:worker_detail", args=[self.object.worker.pk])


class LearnerUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Редактирование обучаемого"""

    model = Worker
    fields = []
    template_name = "learning/learner_form.html"
    permission_required = 'learning.change_learner'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        LearnerFormSet = inlineformset_factory(Worker, Learner, form=LearnerForm, extra=0, can_delete=False)

        if self.request.POST:
            context["formset"] = LearnerFormSet(self.request.POST, instance=self.object)
        else:
            context["formset"] = LearnerFormSet(instance=self.object)

        return context

    def _sync_knowledge_date(self, worker):
        for learner in worker.learner.all():
            # Текущие направления у learner (объекты Direction)
            current_directions = learner.direction.all()
            # Существующие направления в KnowledgeDate для этого learner
            existing_knowledge_dates = KnowledgeDate.objects.filter(
                learner=learner,
                is_active=True
            )
            existing_directions = {kd.direction for kd in existing_knowledge_dates}

            # 1. Добавляем новые направления
            for direction in current_directions:
                if direction not in existing_directions:
                    KnowledgeDate.objects.create(
                        learner=learner,
                        direction=direction,
                        is_active=True
                    )

            # 2. Деактивируем устаревшие направления
            stale_directions = existing_directions - set(current_directions)
            for direction in stale_directions:
                knowledge_date = existing_knowledge_dates.filter(direction=direction).first()
                if knowledge_date:  # Проверка на существование
                    knowledge_date.is_active = False
                    knowledge_date.save()

    def form_valid(self, form):
        self.object = form.save()

        formset = self.get_context_data()['formset']

        if formset.is_valid():
            formset.save()
            self._sync_knowledge_date(self.object)
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse("organization:worker_detail", args=[self.object.pk])


class LearnerDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Удаление филиала"""

    model = Learner
    permission_required = 'learning.delete_learner'
    success_url = reverse_lazy("organization:organization_list")
