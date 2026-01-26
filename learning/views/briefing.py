from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    UpdateView,
    ListView,
)
from datetime import timedelta
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import Http404
from learning.forms import ProgramBriefingForm, ProgramBriefingNotActive, BriefingDayForm, BulkBriefingDayForm
from learning.models import ProgramBriefing, Exam, Test, BriefingDay, Learner
from django.http import HttpResponseNotFound
from django.db import transaction
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from organization.models import Worker
from organization.views import EntityDetailView


class ProgramBriefingCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Создание программы инструктажа"""

    model = ProgramBriefing
    form_class = ProgramBriefingForm
    permission_required = 'learning.add_programbriefing'

    def form_valid(self, form):
        briefing_program = form.save()
        Test.objects.create(briefing_program=briefing_program)
        Exam.objects.create(briefing_program=briefing_program, total_questions=10)
        return super().form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['model_name'] = self.request.GET.get('model_name')
        context['pk'] = self.request.GET.get('pk')
        return context

    def get_success_url(self):
        return reverse("learning:briefing_program_detail", args=[self.object.pk])


class ProgramBriefingDetailView(DetailView):
    """Просмотр программы инструктажа"""
    model = ProgramBriefing

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['model_name'] = self.request.GET.get('model_name')
        context['pk'] = self.request.GET.get('pk')
        return context


class ProgramBriefingUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Редактирование программы инструктажа"""

    model = ProgramBriefing
    permission_required = 'learning.change_programbriefing'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['model_name'] = self.request.GET.get('model_name')
        context['pk'] = self.request.GET.get('pk')
        return context

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not obj:
            raise Http404("Программа не найдена")
        return obj

    def get_form_class(self):
        if not self.object:
            self.object = self.get_object()
        return ProgramBriefingForm if self.object.is_active else ProgramBriefingNotActive

    def get_success_url(self):
        model_name = self.request.GET.get('model_name')
        pk = self.request.GET.get('pk')
        return reverse("organization:entity_briefing_program", kwargs={'model_name': model_name, 'pk': pk})


class ProgramBriefingDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Удаление программы инструктажа"""

    model = ProgramBriefing
    permission_required = 'learning.delete_programbriefing'
    template_name = "learning/program_confirm_delete.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['model_name'] = self.request.GET.get('model_name')
        context['pk'] = self.request.GET.get('pk')
        return context

    def get_success_url(self):
        model_name = self.request.GET.get('model_name')
        pk = self.request.GET.get('pk')
        return reverse("organization:entity_briefing_program", kwargs={'model_name':model_name, 'pk': pk})


class BriefingDayCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Создание инструктажа"""
    model = BriefingDay
    permission_required = 'learning.add_briefingday'
    form_class = BriefingDayForm

    def form_valid(self, form):
        briefing_day = form.save(commit=False)
        learner = self.kwargs['learner_pk']
        start_date = briefing_day.briefing_day - timedelta(days=30)
        try:
            briefing_day.learner = Learner.objects.get(pk=learner)
            if not briefing_day.learner.exam_results.filter(
                    exam__briefing_program=briefing_day.briefing_program,
                    test_date__gte=start_date,
                    test_date__lte=briefing_day.briefing_day,
                    is_passed=True
            ).exists():
                form.add_error(
                    None,
                    f'{briefing_day.learner} не сдал тестирование по программе {briefing_day.briefing_program}'
                )
                return self.form_invalid(form)
            else:
                briefing_day.save()
            return super().form_valid(form)
        except Learner.DoesNotExist:
            return HttpResponseNotFound("Работник не найден")

    def get_success_url(self):
        model_name = self.request.GET.get('model_name')
        pk = self.request.GET.get('pk')
        return reverse("organization:entity_briefing_program", kwargs={'model_name': model_name, 'pk': pk})


class BriefingDayUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Редактирование инструктажа"""
    model = BriefingDay
    form_class = BriefingDayForm
    permission_required = 'learning.change_briefingday'

    def get_success_url(self):
        if self.request.GET.get("archive") == "1":
            return reverse("learning:briefing_day_list", args=[self.object.learner.worker.pk])
        else:
            return reverse("organization:worker_detail", args=[self.object.learner.worker.pk])


class BriefingDayListView(ListView):
    """Просмотр архива инструктажей"""
    model = BriefingDay
    paginate_by = 20

    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)
        learner = Learner.objects.filter(worker__pk=self.kwargs['worker_pk'])
        queryset = queryset.filter(learner__in=learner)
        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['worker_pk'] = self.kwargs['worker_pk']
        context['worker'] = Worker.objects.filter(pk=self.kwargs['worker_pk']).first()
        return context


class BriefingDayDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Удаление инструктажа"""

    model = BriefingDay
    permission_required = 'learning.delete_briefingday'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        if self.request.GET.get("archive") == "1":
            context['is_archive'] = True
        else:
            context['is_archive'] = False
        return context

    def get_success_url(self):
        if self.request.GET.get("archive") == "1":
            return reverse("learning:briefing_day_list", args=[self.kwargs['worker_pk']])
        else:
            return reverse("organization:worker_detail", args=[self.kwargs['worker_pk']])


@login_required
@permission_required('learning.add_programbriefing', raise_exception=True)
def create_bulk_briefing_day(request):
    """Массовое проведение инструктажа работникам"""
    model_name = request.GET.get('model_name')
    pk = request.GET.get('pk')
    if request.method == 'POST':
        form = BulkBriefingDayForm(request.POST)
        try:
            with transaction.atomic():
                if form.is_valid():
                    briefings = form.save()
                    return redirect(
                        'organization:district_detail',
                        pk=request.user.worker.district.pk
                    )
        except ValidationError:
            pass
        except Exception as e:
            form.add_error(None, f"Ошибка при сохранении данных {e}.")
    else:
        form = BulkBriefingDayForm()
    return render(request, 'learning/bulk_briefing_day_form.html',
                  {'form': form,
                   'model_name': model_name,
                   'pk': pk})


class BriefingLogListView(EntityDetailView):
    """Просмотр журнала инструктажа"""
    template_name = 'learning/briefing_log.html'
    paginate_by = 10

    def get_briefingday_queryset(self, entity_obj):
        model_name = self.kwargs['model_name']

        if model_name == 'organization':
            workers = Worker.objects.filter(organization=entity_obj)
            learners = Learner.objects.filter(worker__in=workers)
            return BriefingDay.objects.filter(learner__in=learners)
        elif model_name == 'branch':
            workers = Worker.objects.filter(branch=entity_obj)
            learners = Learner.objects.filter(worker__in=workers)
            return BriefingDay.objects.filter(learner__in=learners)
        elif model_name == 'division':
            workers = Worker.objects.filter(division=entity_obj)
            learners = Learner.objects.filter(worker__in=workers)
            return BriefingDay.objects.filter(learner__in=learners)
        elif model_name == 'district':
            workers = Worker.objects.filter(district=entity_obj)
            learners = Learner.objects.filter(worker__in=workers)
            return BriefingDay.objects.filter(learner__in=learners)
        elif model_name == 'group':
            workers = Worker.objects.filter(group=entity_obj)
            learners = Learner.objects.filter(worker__in=workers)
            return BriefingDay.objects.filter(learner__in=learners)
        else:
            return BriefingDay.objects.none()

    def get_search_params(self):
        """Собираем все параметры поиска из GET."""
        params = super().get_search_params()
        params.update({
            'briefing_type': self.request.GET.get('briefing_type', ''),
            'briefing_program': self.request.GET.get('briefing_program', ''),
            'briefing_reason': self.request.GET.get('briefing_reason', ''),
            'next_date_from': self.request.GET.get('next_date_from', ''),
            'next_date_to': self.request.GET.get('next_date_to', ''),
        })
        return params

    def get_filter(self, queryset, search_params):
        """Применяет фильтры к queryset на основе параметров поиска."""
        if not search_params:
            return queryset

        filters = {}
        FILTER_MAP = {
            'surname': 'learner__worker__surname__icontains',
            'briefing_type': 'briefing_type__briefing_type',
            'briefing_program': 'briefing_program__name__icontains',
            'date_briefing_from': 'briefing_day__gte',
            'date_briefing_to': 'briefing_day__lte',
            'briefing_reason': 'briefing_reason__icontains',
            'next_date_from': 'next_briefing_day__gte',
            'next_date_to': 'next_briefing_day__lte',
        }

        for param_name, filter_key in FILTER_MAP.items():
            value = search_params.get(param_name)
            if value is not None and value != '':
                filters[filter_key] = value

        return queryset.filter(**filters)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_params = self.get_search_params()
        context['search_params'] = search_params

        # Проверяем, что объект существует
        if not self.object:
            return context

        # Получаем инструктажи для текущей сущности
        briefing_day_list = self.get_briefingday_queryset(self.object)

        # Применяем фильтры
        briefing_day_list = self.get_filter(briefing_day_list, search_params)
        # Сортируем
        briefing_day_list = briefing_day_list.order_by('learner', '-briefing_day')

        # Пагинируем
        briefing_day_page = self.get_paginated_page(briefing_day_list, 'briefing_day_page')
        context['briefing_day_page'] = briefing_day_page

        return context

