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
from learning.models import Learner
from django.utils.datastructures import MultiValueDictKeyError
from organization.forms import WorkerCreateForm, WorkerUpdateForm, PositionForm
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
        PositionFormSet = inlineformset_factory(
            Worker,  # Родительская модель (владелец)
            Position,  # Дочерняя модель (позиции)
            form=PositionForm,
            fields=["name", "is_main"],
            extra=1,
        )

        if self.request.POST:
            # При POST: передаём instance (пока None) и пустой queryset
            context['position_formset'] = PositionFormSet(
                self.request.POST,
                instance=None,  # Будет заполнен позже
                queryset=Position.objects.none()
            )
        else:
            # При GET: пустой FormSet
            context['position_formset'] = PositionFormSet(
                instance=None,
                queryset=Position.objects.none()
            )

        return context

    @transaction.atomic
    def form_valid(self, form):
        try:
            organization_pk = self.request.GET.get("organization")
            branch_pk = self.request.GET.get("branch")
            division_pk = self.request.GET.get("division")
            district_pk = self.request.GET.get("district")
            group_pk = self.request.GET.get("group")

            worker = form.save(commit=False)

            worker.organization = Organization.objects.get(pk=organization_pk)
            worker.branch = Branch.objects.get(pk=branch_pk)
            worker.division = Division.objects.get(pk=division_pk)
            worker.district = District.objects.get(pk=district_pk)

            if group_pk:
                worker.group = Group.objects.get(pk=group_pk)
            else:
                worker.group = None

            worker.save()

            PositionFormSet = inlineformset_factory(
                Worker,
                Position,
                form=PositionForm,
                fields=["name", "is_main"],
                extra=1,
            )
            position_formset = PositionFormSet(
                self.request.POST,
                instance=worker,
                queryset=Position.objects.filter(worker=worker)
            )

            if position_formset.is_valid():
                position_formset.save()
                for position in worker.position.all():
                    learner = Learner.objects.create(worker=worker, position=position)
                return super().form_valid(form)
            else:
                transaction.set_rollback(True)
                return self.form_invalid(form)


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
        PositionFormSet = inlineformset_factory(
            Worker,
            Position,
            form=PositionForm,
            fields=["name", "is_main"],
            extra=1,
            can_delete=True
        )

        if self.request.POST:
            context['position_formset'] = PositionFormSet(
                self.request.POST,
                instance=self.object,
                queryset=Position.objects.filter(worker=self.object)
            )
        else:
            context['position_formset'] = PositionFormSet(
                instance=self.object,
                queryset=Position.objects.filter(worker=self.object)
            )

        return context

    @transaction.atomic
    def form_valid(self, form):
        self.object = form.save()
        context = self.get_context_data()
        position_formset = context['position_formset']

        if position_formset.is_valid():
            position_formset.save()
            self._sync_learners(self.object)  # Синхронизация Learner
            return super().form_valid(form)
        else:
            transaction.set_rollback(True)
            return self.form_invalid(form)

    def _sync_learners(self, worker):
        current_positions = set(worker.position.all())
        existing_learners = Learner.objects.filter(worker=worker)
        existing_positions = {learner.position for learner in existing_learners}

        # Создаём Learner для новых позиций
        for position in current_positions:
            if position not in existing_positions:
                Learner.objects.create(worker=worker, position=position)



class WorkerDeleteView(DeleteView):
    """Удаление работника"""

    model = Worker

    def get_success_url(self):
        district_pk = self.request.GET["district"]
        return reverse("organization:district_detail", args=[district_pk])
