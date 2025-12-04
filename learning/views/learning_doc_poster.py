from django.urls import reverse
from django.views.generic import UpdateView
from django.forms import inlineformset_factory
from learning.forms import LearningDocForm, LearningPosterForm
from learning.models import LearningPoster, LearningDoc, Program


class LearningDocUpdateView(UpdateView):
    """Обновление/добавление/удаление документов обучения"""
    model = Program
    fields = []
    template_name = "learning/learning_doc.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        LearningDocFormSet = inlineformset_factory(
            Program,
            LearningDoc,
            form=LearningDocForm,
            extra=1,
            can_delete=True
        )

        if self.request.POST:
            context['learning_doc_formset'] = LearningDocFormSet(
                self.request.POST,
                self.request.FILES,
                instance=self.object
            )
        else:
            context['learning_doc_formset'] = LearningDocFormSet(instance=self.object)

        return context

    def form_valid(self, form):
        context = self.get_context_data()
        learning_doc_formset = context['learning_doc_formset']

        if learning_doc_formset.is_valid():
            self.object = form.save()
            learning_doc_formset.instance = self.object
            learning_doc_formset.save()
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse("learning:program_detail", args=[self.object.pk])


class LearningPosterUpdateView(UpdateView):
    """Обновление/добавление/удаление плакатов обучения"""
    model = Program
    fields = []
    template_name = "learning/learning_poster.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        LearningPosterFormSet = inlineformset_factory(
            Program,
            LearningPoster,
            form=LearningPosterForm,
            extra=1,
            can_delete=True
        )

        if self.request.POST:
            context['learning_poster_formset'] = LearningPosterFormSet(
                self.request.POST,
                self.request.FILES,
                instance=self.object

            )
        else:
            context['learning_poster_formset'] = LearningPosterFormSet(instance=self.object)

        return context

    def form_valid(self, form):
        context = self.get_context_data()
        learning_poster_formset = context['learning_poster_formset']

        if learning_poster_formset.is_valid():
            self.object = form.save()
            learning_poster_formset.instance = self.object
            learning_poster_formset.save()
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse("learning:program_detail", args=[self.object.pk])


