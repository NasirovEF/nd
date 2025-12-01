from django.views.generic import CreateView
from django.shortcuts import reverse
from learning.models import Test, Question, Answer
from learning.forms import TestForm, QuestionFormSet, AnswerFormSets
from typing import Optional, Dict, List
from django.contrib import messages
from django.db import transaction
from django.forms.utils import ErrorList
from django.http import HttpResponse


class TestCreateView(CreateView):
    model = Test
    form_class = TestForm

    def get_question_formset(self, data: Optional[Dict] = None, files: Optional[Dict] = None) -> QuestionFormSet:
        """
        Возвращает формасет вопросов, отфильтрованный по наличию данных в POST.
        """
        formset = QuestionFormSet(
            data=data,
            files=files,
            instance=self.object or Test(),
            prefix='questions'
        )

        if data:
            total_forms = int(data.get('questions-TOTAL_FORMS', 0))
            valid_forms = []
            for i in range(total_forms):
                text_key = f'questions-{i}-text'
                if text_key in data and data[text_key]:  # проверяем наличие и непустоту
                    valid_forms.append(formset.forms[i])
            formset.forms = valid_forms
            formset._total_form_count = len(valid_forms)

        return formset

    def _create_answer_formset(
        self,
        q_form,
        data: Optional[Dict] = None,
        files: Optional[Dict] = None
    ) -> AnswerFormSets:
        """
        Создаёт формасет ответов для конкретного вопроса.
        """
        answer_prefix = f'{q_form.prefix}-answers'
        return AnswerFormSets(
            data=data,
            files=files,
            instance=q_form.instance,
            prefix=answer_prefix
        )

    def get_context_data(self, **kwargs) -> Dict:
        context = super().get_context_data(**kwargs)
        question_formset = kwargs.get('question_formset')
        answer_formsets = kwargs.get('answer_formsets')

        if self.request.method == 'POST':
            if question_formset is None:
                question_formset = self.get_question_formset(
                    data=self.request.POST,
                    files=self.request.FILES
                )
            context['question_formset'] = question_formset

            if answer_formsets is not None:
                for q_form, a_formset in zip(question_formset.forms, answer_formsets):
                    q_form.answer_formset = a_formset
            else:
                for q_form in question_formset:
                    q_form.answer_formset = self._create_answer_formset(
                        q_form,
                        data=self.request.POST,
                        files=self.request.FILES
                    )
        else:
            if question_formset is None:
                question_formset = self.get_question_formset()
            context['question_formset'] = question_formset

            for q_form in question_formset:
                q_form.answer_formset = self._create_answer_formset(q_form)

        return context

    @transaction.atomic
    def form_valid(self, form) -> HttpResponse:
        question_formset = self.get_question_formset(
            data=self.request.POST,
            files=self.request.FILES
        )

        if not question_formset.is_valid():
            return self.render_to_response(
                self.get_context_data(form=form, question_formset=question_formset)
            )

        all_answer_formsets: List[AnswerFormSets] = []
        has_errors = False  # Флаг: есть ли хоть одна ошибка

        for q_form in question_formset:
            answer_formset = self._create_answer_formset(
                q_form,
                data=self.request.POST,
                files=self.request.FILES
            )

            # 1. Проверяем валидность formset'а
            if not answer_formset.is_valid():
                has_errors = True

            # 2. Проверяем логику "ровно один правильный ответ"
            correct_count = sum(
                1 for f in answer_formset.forms
                if f.cleaned_data.get('is_correct', False)
            )
            if correct_count == 0:
                answer_formset._non_form_errors = ErrorList([
                    "Для вопроса должен быть выбран ровно один правильный ответ."
                ])
                has_errors = True
            elif correct_count > 1:
                answer_formset._non_form_errors = ErrorList([
                    "Нельзя выбрать более одного правильного ответа."
                ])
                has_errors = True

            all_answer_formsets.append(answer_formset)  # Добавляем ВСЕГДА

        # 3. Если есть ошибки — возвращаем контекст со всеми formset'ами
        if has_errors:
            return self.render_to_response(
                self.get_context_data(
                    form=form,
                    question_formset=question_formset,
                    answer_formsets=all_answer_formsets
                )
            )

        # 4. Если нет ошибок — сохраняем данные
        try:
            self.object = form.save()
            questions = question_formset.save(commit=False)
            for question in questions:
                question.test = self.object
                question.save()

            for question, answer_formset in zip(questions, all_answer_formsets):
                answer_formset.instance = question
                answer_formset.save()

            return super().form_valid(form)

        except Exception as e:
            messages.error(self.request, f"Ошибка сохранения: {str(e)}")
            return self.render_to_response(
                self.get_context_data(
                    form=form,
                    question_formset=question_formset,
                    answer_formsets=all_answer_formsets
                )
            )

    def form_invalid(self, form) -> HttpResponse:
        question_formset = self.get_question_formset(
            data=self.request.POST,
            files=self.request.FILES
        )
        question_formset.is_valid()

        all_answer_formsets: List[AnswerFormSets] = []
        for q_form in question_formset:
            answer_formset = self._create_answer_formset(
                q_form,
                data=self.request.POST,
                files=self.request.FILES
            )
            answer_formset.is_valid()  # Запускаем валидацию
            all_answer_formsets.append(answer_formset)  # Добавляем всегда

        return self.render_to_response(
            self.get_context_data(
                form=form,
                question_formset=question_formset,
                answer_formsets=all_answer_formsets
            )
        )

    def get_success_url(self) -> str:
        return reverse("organization:organization_list")
