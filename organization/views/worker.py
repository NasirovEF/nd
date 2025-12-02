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
from learning.models import Learner, KnowledgeDate
from django.utils.datastructures import MultiValueDictKeyError

from learning.models.learner_direction import StaffDirection, Direction
from organization.forms import WorkerCreateForm, WorkerUpdateForm, PositionForm, PositionFormSet
from organization.models import Worker, District, Group, Organization, Branch, Division, Position
from django.forms import inlineformset_factory
from django.db import transaction


class WorkerListView(ListView):
    """Просмотр списка работников"""
    model = Worker


class WorkerDetailView(DetailView):
    """Просмотр одной из работников"""

    model = Worker

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class WorkerCreateView(CreateView):
    model = Worker
    form_class = WorkerCreateForm

    def get_success_url(self):
        return reverse("organization:district_detail", args=[self.object.district.pk])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Если формсет ещё не создан (GET-запрос или повторная отрисовка с ошибками)
        if 'position_formset' not in context:
            PositionFormSetClass = inlineformset_factory(
                Worker,
                Position,
                form=PositionForm,
                formset=PositionFormSet,
                fields=["name", "is_main"],
                extra=1,
                can_delete=False,
            )
            # Для GET: instance=None; для POST с ошибкой: instance=worker (если есть)
            instance = self.object if self.object else None
            context['position_formset'] = PositionFormSetClass(instance=instance)

        return context

    @transaction.atomic
    def form_valid(self, form):
        try:
            # 1. Заполняем поля работника
            worker = form.save(commit=False)
            worker.organization = Organization.objects.get(pk=self.request.GET.get("organization"))
            worker.branch = Branch.objects.get(pk=self.request.GET.get("branch"))
            worker.division = Division.objects.get(pk=self.request.GET.get("division"))
            worker.district = District.objects.get(pk=self.request.GET.get("district"))
            worker.group = Group.objects.get(pk=self.request.GET.get("group")) if self.request.GET.get(
                "group") else None

            # 2. Сохраняем работника (обязательно!)
            worker.save()
            self.object = worker  # ← критически важно для контекста

            # 3. Создаём формсет с POST-данными и привязанным instance
            PositionFormSetClass = inlineformset_factory(
                Worker,
                Position,
                form=PositionForm,
                formset=PositionFormSet,
                fields=["name", "is_main"],
                extra=1,
                can_delete=False,
            )
            position_formset = PositionFormSetClass(
                self.request.POST,
                instance=worker,  # ← instance=worker (уже сохранён)
            )

            # 4. Валидируем и сохраняем формсет
            if position_formset.is_valid():
                position_formset.save(commit=True)  # ← commit=True обязательно!

                # 5. Создаём Learner для всех позиций
                for position in worker.position.all():
                    try:
                        staff_direction = StaffDirection.objects.get(position=position.name)
                        directions = staff_direction.direction.all()
                    except StaffDirection.DoesNotExist:
                        directions = Direction.objects.none()  # пустой QuerySet

                    learner = Learner.objects.create(
                        worker=worker,
                        position=position
                    )
                    learner.direction.set(directions)
                    for direction in directions:
                        KnowledgeDate.objects.create_or_update_active(learner=learner, direction=direction)
                return super().form_valid(form)
            else:
                # 6. Если формсет невалиден — показываем ошибки
                context = self.get_context_data()
                context['form'] = form
                context['position_formset'] = position_formset
                transaction.set_rollback(True)
                return self.render_to_response(context)

        except Exception as e:
            transaction.set_rollback(True)
            return self.form_invalid(form)


class WorkerUpdateView(UpdateView):
    model = Worker
    form_class = WorkerUpdateForm

    def get_success_url(self):
        return reverse("organization:district_detail", args=[self.object.district.pk])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        PositionFormSets = inlineformset_factory(
            Worker,
            Position,
            form=PositionForm,
            formset=PositionFormSet,  # Ваш кастомный формсет с clean()
            fields=["name", "is_main"],
            extra=1,
            can_delete=True,  # Разрешаем удаление позиций
        )

        if self.request.POST:
            context['position_formset'] = PositionFormSets(
                self.request.POST,
                instance=self.object,
            )
        else:
            context['position_formset'] = PositionFormSets(instance=self.object)

        return context

    @transaction.atomic
    def form_valid(self, form):
        self.object = form.save()
        context = self.get_context_data()
        position_formset = context['position_formset']

        if position_formset.is_valid():
            position_formset.save()
            self._sync_learners(self.object)  # Создаём новые Learner, старые оставляем
            return super().form_valid(form)
        else:
            transaction.set_rollback(True)
            return self.form_invalid(form)

    def _sync_learners(self, worker):
        current_positions = worker.position.all()
        existing_learner_positions = set(
            Learner.objects.filter(worker=worker)
            .values_list('position', flat=True)
        )

        for position in current_positions:
            if position.pk not in existing_learner_positions:
                try:
                    staff_direction = StaffDirection.objects.get(position=position.name)
                    directions = staff_direction.direction.all()
                except StaffDirection.DoesNotExist:
                    directions = Direction.objects.none()  # пустой QuerySet

                learner = Learner.objects.create(
                    worker=worker,
                    position=position
                )
                learner.direction.set(directions)
                for direction in directions:
                    KnowledgeDate.objects.create_or_update_active(learner=learner, direction=direction)


class WorkerDeleteView(DeleteView):
    """Удаление работника"""

    model = Worker

    def get_success_url(self):
        district_pk = self.request.GET["district"]
        return reverse("organization:district_detail", args=[district_pk])
