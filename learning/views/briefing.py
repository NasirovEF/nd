from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    UpdateView,
    ListView,
)
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import Http404
from learning.forms import ProgramBriefingForm, ProgramBriefingNotActive, BriefingDayForm, BulkBriefingDayForm
from learning.models import ProgramBriefing, Exam, Test, BriefingDay, Learner
from django.http import HttpResponseNotFound


class ProgramBriefingCreateView(CreateView):
    """Создание программы инструктажа"""

    model = ProgramBriefing
    form_class = ProgramBriefingForm

    def form_valid(self, form):
        briefing_program = form.save()
        Test.objects.create(briefing_program=briefing_program)
        Exam.objects.create(briefing_program=briefing_program, total_questions=10)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("learning:briefing_program_detail", args=[self.object.pk])


class ProgramBriefingDetailView(DetailView):
    """Просмотр программы инструктажа"""
    model = ProgramBriefing


class ProgramBriefingUpdateView(UpdateView):
    """Редактирование программы инструктажа"""

    model = ProgramBriefing

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


class ProgramBriefingDeleteView(DeleteView):
    """Удаление программы инструктажа"""

    model = ProgramBriefing
    template_name = "learning/program_confirm_delete.html"

    def get_success_url(self):
        return reverse("organization:district_detail", args=[self.request.GET["district"]])


class BriefingDayCreateView(CreateView):
    """Создание инструктажа"""
    model = BriefingDay
    form_class = BriefingDayForm

    def form_valid(self, form):
        briefing_day = form.save(commit=False)
        learner = self.kwargs['learner_pk']
        try:
            briefing_day.learner = Learner.objects.get(pk=learner)
            briefing_day.save()
            return super().form_valid(form)
        except Learner.DoesNotExist:
            return HttpResponseNotFound("Работник не найден")

    def get_success_url(self):
        return reverse("organization:worker_detail", args=[self.object.learner.worker.pk])


class BriefingDayUpdateView(UpdateView):
    """Редактирование инструктажа"""
    model = BriefingDay
    form_class = BriefingDayForm

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


class BriefingDayDeleteView(DeleteView):
    """Удаление инструктажа"""

    model = BriefingDay

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


def create_bulk_briefing_day(request):
    """Массовое проведение инструктажа работникам"""
    if request.method == 'POST':
        form = BulkBriefingDayForm(request.POST)
        if form.is_valid():
            briefing_day = form.save()
            return redirect('organization:district_detail', args=[request.user.worker.district.pk])
    else:
        form = BulkBriefingDayForm()
    return render(request, 'learning/bulk_briefing_day_form.html', {'form': form})

