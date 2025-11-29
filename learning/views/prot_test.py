from django.views.generic import CreateView
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from learning.models import Test, Question, Answer
from learning.forms import TestForm, QuestionFormSet, AnswerFormSet


class TestCreateView(CreateView):
    model = Test
    form_class = TestForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 1. Инициализируем QuestionFormSet с 20 пустыми формами
        if self.request.POST:
            context['question_formset'] = QuestionFormSet(
                self.request.POST,
                instance=self.object,
                prefix='questions'
            )
        else:
            # Создаём 20 пустых форм вопросов
            context['question_formset'] = QuestionFormSet(
                instance=self.object or Test(),
                queryset=Question.objects.none(),  # пустые формы
                prefix='questions'  # фиксированный префикс
            )

        # 2. Для каждого вопроса — AnswerFormSet с 3 пустыми ответами
        for q_form in context['question_formset'].forms:
            if self.request.POST:
                # При POST берём данные из запроса
                q_form.answer_formset = AnswerFormSet(
                    self.request.POST,
                    instance=q_form.instance,
                    prefix=f'questions-{q_form.prefix}-answers'  # фиксированный шаблон
                )
            else:
                # При GET — 3 пустые формы ответов
                q_form.answer_formset = AnswerFormSet(
                    instance=q_form.instance,
                    queryset=Answer.objects.none(),
                    prefix=f'questions-{q_form.prefix}-answers'  # фиксированный префикс
                )

        return context

    def form_valid(self, form):
        # Сохраняем основной объект (тест)
        self.object = form.save()

        # Обрабатываем формсет вопросов
        question_formset = QuestionFormSet(self.request.POST, instance=self.object)
        if question_formset.is_valid():
            questions = question_formset.save()

            # Для каждого вопроса сохраняем ответы
            for question in questions:
                answer_formset = AnswerFormSet(self.request.POST, instance=question)
                if answer_formset.is_valid():
                    answer_formset.save()
                else:
                    # Если ответы невалидны — откатываем всё
                    return self.form_invalid(form)
        else:
            return self.form_invalid(form)

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return '/tests/'  # ваш URL успеха
