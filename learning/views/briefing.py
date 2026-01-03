from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    UpdateView,
)
from django.urls import reverse
from django.http import Http404
from learning.forms import ProgramBriefingForm, ProgramBriefingNotActive
from learning.models import ProgramBriefing, Exam, Test


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