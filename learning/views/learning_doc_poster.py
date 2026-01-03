from django.urls import reverse
from django.views.generic import UpdateView
from learning.forms import LearningDocForm, LearningPosterForm
from learning.models import LearningPoster, LearningDoc, Program, ProgramBriefing
from django.forms import modelformset_factory
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from django.http import Http404


class LearningDocUpdateView(UpdateView):
    fields = []  # Не используем поля модели напрямую
    template_name = "learning/learning_doc.html"

    def dispatch(self, request, *args, **kwargs):
        # Сначала проверяем kwargs (из URL)
        self.model_class = self.kwargs.get('model_class')

        # Если не найдено — берём из аргументов представления (как в ваших URL)
        if self.model_class is None:
            self.model_class = getattr(self, 'model_class', None)

        if not self.model_class:
            raise Http404("Model class not specified")

        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        # Получаем объект по PK
        return get_object_or_404(self.model_class, pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        content_type = ContentType.objects.get_for_model(self.object)
        learning_docs = LearningDoc.objects.filter(
            content_type=content_type,
            object_id=self.object.pk
        )

        LearningDocFormSet = modelformset_factory(
            LearningDoc,
            form=LearningDocForm,
            extra=1,
            can_delete=True
        )

        if self.request.POST:
            context['learning_doc_formset'] = LearningDocFormSet(
                self.request.POST,
                self.request.FILES,
                queryset=learning_docs
            )
        else:
            context['learning_doc_formset'] = LearningDocFormSet(queryset=learning_docs)

        context['object'] = self.object
        if self.model_class == Program:
            context['model_class'] = "program"
        elif self.model_class == ProgramBriefing:
            context['model_class'] = "program_briefing"
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        learning_doc_formset = context['learning_doc_formset']

        if learning_doc_formset.is_valid():
            self.object = form.save()

            instances = learning_doc_formset.save(commit=False)
            for instance in instances:
                instance.content_type = ContentType.objects.get_for_model(self.object)
                instance.object_id = self.object.pk
                instance.save()

            for obj in learning_doc_formset.deleted_objects:
                obj.delete()

            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        if self.model_class == Program:
            return reverse('learning:program_docs', kwargs={'pk': self.object.pk})
        elif self.model_class == ProgramBriefing:
            return reverse('learning:briefing_docs', kwargs={'pk': self.object.pk})


class LearningPosterUpdateView(UpdateView):
    fields = []  # Не используем поля модели напрямую
    template_name = "learning/learning_poster.html"

    def dispatch(self, request, *args, **kwargs):
        # Сначала проверяем kwargs (из URL)
        self.model_class = self.kwargs.get('model_class')

        # Если не найдено — берём из аргументов представления (как в ваших URL)
        if self.model_class is None:
            self.model_class = getattr(self, 'model_class', None)

        if not self.model_class:
            raise Http404("Model class not specified")

        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        # Получаем объект по PK
        return get_object_or_404(self.model_class, pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        content_type = ContentType.objects.get_for_model(self.object)
        learning_posters = LearningPoster.objects.filter(
            content_type=content_type,
            object_id=self.object.pk
        )

        LearningPosterFormSet = modelformset_factory(
            LearningPoster,
            form=LearningPosterForm,
            extra=1,
            can_delete=True
        )

        if self.request.POST:
            context['learning_poster_formset'] = LearningPosterFormSet(
                self.request.POST,
                self.request.FILES,
                queryset=learning_posters
            )
        else:
            context['learning_poster_formset'] = LearningPosterFormSet(queryset=learning_posters)

        context['object'] = self.object
        if self.model_class == Program:
            context['model_class'] = "program"
        elif self.model_class == ProgramBriefing:
            context['model_class'] = "program_briefing"
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        learning_poster_formset = context['learning_poster_formset']

        if learning_poster_formset.is_valid():
            self.object = form.save()

            instances = learning_poster_formset.save(commit=False)
            for instance in instances:
                instance.content_type = ContentType.objects.get_for_model(self.object)
                instance.object_id = self.object.pk
                instance.save()

            for obj in learning_poster_formset.deleted_objects:
                obj.delete()

            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        if self.model_class == Program:
            return reverse('learning:program_posters', kwargs={'pk': self.object.pk})
        elif self.model_class == ProgramBriefing:
            return reverse('learning:briefing_posters', kwargs={'pk': self.object.pk})

