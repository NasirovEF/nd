from django.views.generic import CreateView, UpdateView, ListView, DeleteView
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.db import transaction
from learning.forms import QuestionForm, AnswerFormSets
from learning.models import Question, Answer, Test
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin


class QuestionListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """Просмотр списка вопросов"""
    model = Question
    permission_required = 'learning.view_question'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        test_pk = self.kwargs['test_pk']
        test = get_object_or_404(Test, pk=test_pk)
        context['test'] = test
        context['search_params'] = {
            'question_text': self.request.GET.get('question_text', ''),}
        return context

    def get_queryset(self):
        test_pk = self.kwargs['test_pk']
        queryset = super().get_queryset()
        queryset = queryset.filter(test__pk=test_pk)
        question_text = self.request.GET.get("question_text")
        if question_text:
            queryset = queryset.filter(text__icontains=question_text)
        return queryset


class QuestionDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Удаление вопроса"""

    model = Question
    permission_required = 'learning.delete_question'

    def get_success_url(self):
        return reverse("learning:question_list", args=[self.request.GET.get("test_pk")])


class QuestionCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Question
    form_class = QuestionForm
    permission_required = 'learning.add_question'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.object.test.direction.is_verbal:
            # Для GET-запроса: пустой формсет без instance
            if not self.request.POST:
                context['answer_formset'] = AnswerFormSets()
            else:
                # Для POST: создаём формсет с данными из запроса, но без instance (пока нет объекта)
                context['answer_formset'] = AnswerFormSets(self.request.POST)

            # Явно указываем, что это CreateView (важно для шаблона при ошибках)
            context['is_create_view'] = True
            context['test'] = get_object_or_404(Test, pk= self.kwargs['test_pk'])
        return context

    @transaction.atomic
    def form_valid(self, form):
        # Получаем test_pk из URL
        test_pk = self.kwargs['test_pk']
        test = get_object_or_404(Test, pk=test_pk)

        # Создаём объект вопроса, но не сохраняем в БД
        self.object = form.save(commit=False)
        self.object.test = test

        if not self.object.test.direction.is_verbal:
            # Создаём формсет ответов (без сохранения)
            answer_formset = AnswerFormSets(
                self.request.POST,
                instance=self.object  # instance есть, но объект ещё не в БД!
            )

            # Валидируем ОБА компонента
            if not (form.is_valid() and answer_formset.is_valid()):
                # Если хоть что-то невалидно — показываем ошибки
                context = self.get_context_data()
                context['form'] = form
                context['answer_formset'] = answer_formset
                return self.render_to_response(context)

            # Теперь сохраняем ВСЁ разом (в транзакции)
            self.object.save()  # Сохраняем вопрос
            answer_formset.save()  # Сохраняем ответы

        # Сохраняем действие для get_success_url
        self.submitted_action = self.request.POST.get('action')

        return super().form_valid(form)

    def get_success_url(self):
        action = self.submitted_action

        if action == 'save_and_add':
            # Переход к созданию нового вопроса для того же теста
            return reverse(
                'learning:question_create',
                args=[self.kwargs['test_pk']]
            )
        else:
            # Обычная кнопка "Сохранить" → список вопросов
            return reverse(
                'learning:question_list',
                args=[self.object.test.pk]
            )


class QuestionUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Обновление вопроса"""
    model = Question
    form_class = QuestionForm
    permission_required = 'larning.change_question'

    def get_object(self, queryset=None):
        self.object = get_object_or_404(Question, pk=self.kwargs['pk'])
        return self.object

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.object.test.direction.is_verbal:
            if 'answer_formset' not in context:
                existing_answers = Answer.objects.filter(question=self.object).order_by('id')
                context['answer_formset'] = AnswerFormSets(
                    instance=self.object,
                    prefix='answers',
                    queryset=existing_answers
                )
        return context

    @transaction.atomic
    def form_valid(self, form):
        self.object = form.save()
        if not self.object.test.direction.is_verbal:
            existing_answers = Answer.objects.filter(question=self.object).order_by('id')

            answer_formset = AnswerFormSets(
                self.request.POST,
                instance=self.object,
                prefix='answers',
                queryset=existing_answers
            )

            if answer_formset.is_valid():
                answer_formset.save()
                return super().form_valid(form)
            else:
                context = self.get_context_data(form=form)
                context['answer_formset'] = answer_formset
                return self.render_to_response(context)

    def get_success_url(self):
        return reverse("learning:question_list", args=[self.object.test.pk])

