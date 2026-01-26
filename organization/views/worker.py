from django.urls import reverse
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)
from learning.models import Learner, KnowledgeDate, Briefing
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from learning.models.learner_direction import StaffDirection, Direction
from organization.forms import WorkerCreateForm, WorkerUpdateForm, PositionForm, PositionFormSet
from organization.models import Worker, Position
from django.forms import inlineformset_factory
from django.db import transaction
from users.models import User


class WorkerListView(ListView):
    """Просмотр списка работников"""
    model = Worker


class WorkerDetailView(DetailView):
    """Просмотр одной из работников"""

    model = Worker

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['briefings'] = Briefing.objects.all()
        context['model_name'] = self.request.GET.get('model_name')
        context['pk'] = self.request.GET.get('pk')
        return context


class WorkerCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Создание работника"""
    model = Worker
    form_class = WorkerCreateForm
    permission_required = 'organization.add_worker'
    template_name = 'organization/worker_form.html'

    def get_success_url(self):
        model_name = self.request.GET.get('model_name')
        pk = self.request.GET.get('pk')
        return reverse("organization:entity_detail", kwargs={'model_name': model_name, 'pk': pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = self.request.GET.get('model_name')
        context['pk'] = self.request.GET.get('pk')
        # Ключевое изменение: всегда проверяем POST данные
        if self.request.method == 'POST':
            PositionFormSetClass = inlineformset_factory(
                Worker,
                Position,
                form=PositionForm,
                formset=PositionFormSet,
                fields=["name", "is_main"],
                extra=1,
                can_delete=False,
            )
            # Для POST всегда используем данные из запроса
            instance = self.object if hasattr(self, 'object') and self.object else None
            context['position_formset'] = PositionFormSetClass(
                self.request.POST,
                self.request.FILES,
                instance=instance,
                prefix='positions'
            )
        elif 'position_formset' not in context:
            # Для GET или если формсет ещё не создан
            PositionFormSetClass = inlineformset_factory(
                Worker,
                Position,
                form=PositionForm,
                formset=PositionFormSet,
                fields=["name", "is_main"],
                extra=1,
                can_delete=False,
            )
            context['position_formset'] = PositionFormSetClass(
                instance=self.object,
                prefix='positions'
            )
        return context

    @transaction.atomic
    def form_valid(self, form):
        try:
            # Создаём формсет с POST-данными
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
                self.request.FILES,
                prefix='positions',
                instance=form.instance
            )
            # Проверяем валидность формы и формсета
            if position_formset.is_valid():
                # Сохраняем работника
                worker = form.save()
                self.object = worker

                # Обновляем instance для формсета и сохраняем
                position_formset.instance = worker
                position_formset.save()
                # Создаём Learner для всех позиций
                for position in worker.position.all():
                    try:
                        staff_direction = StaffDirection.objects.get(position=position.name)
                        directions = staff_direction.direction.all()
                    except StaffDirection.DoesNotExist:
                        directions = Direction.objects.none()
                    learner = Learner.objects.create(
                        worker=worker,
                        position=position
                    )
                    learner.direction.set(directions)
                    for direction in directions:
                        KnowledgeDate.objects.create(learner=learner, direction=direction)

                # Создаём пользователя
                user = User.objects.create(worker=worker)
                login_name = user.get_login_name
                user.username = login_name
                service_num = user.service_number or ""
                user.set_password(f"{login_name}{service_num}")
                user.save()

                return super().form_valid(form)
            else:
                # Если формсет невалиден, показываем ошибки
                context = self.get_context_data()
                context['form'] = form
                context['position_formset'] = position_formset
                return self.render_to_response(context)
        except Exception as e:
            # При любой ошибке показываем форму с данными
            transaction.set_rollback(True)
            context = self.get_context_data()
            context['form'] = form
            return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        """
        Переопределяем POST для корректной обработки
        """
        self.object = None
        form = self.get_form()

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        """
        При невалидной форме сохраняем все данные
        """
        context = self.get_context_data()
        context['form'] = form
        return self.render_to_response(context)



class WorkerUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Worker
    form_class = WorkerUpdateForm
    permission_required = 'organization.change_worker'

    def get_success_url(self):
        model_name = self.request.GET.get('model_name')
        pk = self.request.GET.get('pk')
        return reverse("organization:entity_detail", kwargs={'model_name': model_name, 'pk': pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = self.request.GET.get('model_name')
        context['pk'] = self.request.GET.get('pk')

        PositionFormSets = inlineformset_factory(
            Worker,
            Position,
            form=PositionForm,
            formset=PositionFormSet,
            fields=["name", "is_main"],
            extra=1,
            can_delete=True,
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
                    KnowledgeDate.objects.create(learner=learner, direction=direction)


class WorkerDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Удаление работника"""

    model = Worker
    permission_required = 'organization.delete_worker'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = self.request.GET.get('model_name')
        context['pk'] = self.request.GET.get('pk')

        return context

    def get_success_url(self):
        model_name = self.request.GET.get('model_name')
        pk = self.request.GET.get('pk')
        return reverse("organization:entity_detail", kwargs={'model_name': model_name, 'pk': pk})
