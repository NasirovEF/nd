from django.http import Http404
from django.urls import reverse
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
    View,
)
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from learning.forms import ProgramForm, ProgramFormNotActive
from learning.models import Program, Exam


class ProgramListView(ListView):
    """Просмотр списка филиалов"""

    model = Program


class ProgramDetailView(DetailView):
    """Просмотр одного из филиалов"""

    model = Program

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        tests = []
        questions =[]
        for direction in self.object.direction.all():
            if direction.have_sub_direction:
                for subdirection in direction.sub_direction.all():
                    for test in subdirection.test.all():
                        tests.append(test)
            else:
                for test in direction.test.all():
                    tests.append(test)
        for test in tests:
            for question in test.question.all():
                questions.append(question)
        context["tests"] = tests
        context["questions"] = questions
        return context


class ProgramCreateView(CreateView):
    """Создание филиалов"""

    model = Program
    form_class = ProgramForm

    def form_valid(self, form):
        program = form.save()
        Exam.objects.create(program=program)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("learning:program_detail", args=[self.object.pk])


class ProgramUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Редактирование филиалов"""

    model = Program
    permission_required = 'learning.change_program'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not obj:
            raise Http404("Программа не найдена")
        return obj

    def get_form_class(self):
        if not self.object:
            self.object = self.get_object()
        return ProgramForm if self.object.is_active else ProgramFormNotActive

    def get_success_url(self):
        return reverse("learning:program_detail", args=[self.object.pk])


class ProgramDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Удаление филиала"""

    model = Program
    permission_required = 'learning.delete_program'

    def get_success_url(self):
        return reverse("organization:district_detail", args=[self.request.GET["district"]])
