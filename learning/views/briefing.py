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
        return reverse("learning:briefing_program_detail", args=[self.object.pk])


class ProgramBriefingDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Удаление программы инструктажа"""

    model = ProgramBriefing
    permission_required = 'learning.delete_programbriefing'
    template_name = "learning/program_confirm_delete.html"

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
        return reverse("organization:worker_detail", args=[self.object.learner.worker.pk])


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

    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)
        learner = Learner.objects.filter(worker__pk=self.kwargs['worker_pk'])
        queryset = queryset.filter(learner__in=learner)
        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['worker_pk'] = self.kwargs['worker_pk']
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

