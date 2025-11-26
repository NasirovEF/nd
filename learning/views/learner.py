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
from django.forms import inlineformset_factory
from learning.forms import LearnerForm
from learning.models import Learner, Direction
from organization.models import Worker


class LearnerListView(ListView):
    """Просмотр списка филиалов"""

    model = Learner

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        directions = Direction.objects.all()
        context["directions"] = directions
        return context


class LearnerDetailView(DetailView):
    """Просмотр одного из филиалов"""

    model = Learner


class LearnerCreateView(CreateView):
    """Создание филиалов"""

    model = Learner
    form_class = LearnerForm

    def get_success_url(self):
        return reverse("organization:worker_detail", args=[self.object.worker.pk])


class LearnerUpdateView(UpdateView):
    """Редактирование филиалов"""

    model = Worker
    fields = []
    template_name = "learning/learner_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        LearnerFormSet = inlineformset_factory(Worker, Learner, form=LearnerForm, extra=0, can_delete=False)

        if self.request.POST:
            context["formset"] = LearnerFormSet(self.request.POST, instance=self.object)
        else:
            context["formset"] = LearnerFormSet(instance=self.object)

        return context

    def form_valid(self, form):
        self.object = form.save()

        formset = self.get_context_data()['formset']

        if formset.is_valid():
            formset.save()
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse("organization:worker_detail", args=[self.object.pk])


class LearnerDeleteView(DeleteView):
    """Удаление филиала"""

    model = Learner
    success_url = reverse_lazy("organization:organization_list")
