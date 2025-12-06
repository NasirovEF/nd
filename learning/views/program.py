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

from learning.forms import ProgramForm, ProgramFormNotActive
from learning.models import Program, Test


class ProgramListView(ListView):
    """Просмотр списка филиалов"""

    model = Program


class ProgramDetailView(DetailView):
    """Просмотр одного из филиалов"""

    model = Program


class ProgramCreateView(CreateView):
    """Создание филиалов"""

    model = Program
    form_class = ProgramForm

    def form_valid(self, form):
        program = form.save()
        if hasattr(program, 'test') and program.test is not None:
            return super().form_valid(form)
        else:
            Test.objects.create(program=program)
            return super().form_valid(form)

    def get_success_url(self):
        return reverse("learning:program_detail", args=[self.object.pk])


class ProgramUpdateView(UpdateView):
    """Редактирование филиалов"""

    model = Program

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


class ProgramDeleteView(DeleteView):
    """Удаление филиала"""

    model = Program

    def get_success_url(self):
        return reverse("organization:district_detail", args=[self.request.GET["district"]])
