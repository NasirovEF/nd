from django.views.generic import CreateView, UpdateView
from django.shortcuts import reverse
from learning.models import Test, Question, Answer
from learning.forms import TestForm, QuestionFormSet, AnswerFormSets
from typing import Optional, Dict, List
from django.contrib import messages
from django.db import transaction
from django.forms.utils import ErrorList
from django.http import HttpResponse


# class TestCreateView(CreateView):
#     model = Test
#     form_class = TestForm
#
#     def get_question_formset(self, data: Optional[Dict] = None, files: Optional[Dict] = None) -> QuestionFormSet:
#         formset = QuestionFormSet(
#             data=data,
#             files=files,
#             instance=self.object or (self.model() if self.model else None),
#             prefix='questions'
#         )
#
#         if data:
#             total_forms = int(data.get('questions-TOTAL_FORMS', 0))
#             valid_forms = []
#
#             for i in range(total_forms):
#                 form = formset.forms[i]
#                 # Проверяем валидность формы и заполненность text
#                 if form.is_valid() and form.cleaned_data.get('text'):
#                     valid_forms.append(form)
#                 else:
#                     # Инициализируем _non_form_errors, если его нет
#                     if not hasattr(formset, '_non_form_errors') or formset._non_form_errors is None:
#                         formset._non_form_errors = ErrorList()
#                     # Добавляем ошибку
#                     formset._non_form_errors.append(
#                         f"Вопрос {i + 1} не может быть пустым или содержит ошибки."
#                     )
#
#             formset.forms = valid_forms
#             formset._total_form_count = len(valid_forms)
#
#         return formset
#
#     def _create_answer_formset(
#             self,
#             q_form,
#             data: Optional[Dict] = None,
#             files: Optional[Dict] = None
#     ) -> AnswerFormSets:
#         """
#         Создаёт формасет ответов для конкретного вопроса.
#         """
#         answer_prefix = f'{q_form.prefix}-answers'
#         return AnswerFormSets(
#             data=data,
#             files=files,
#             instance=q_form.instance,
#             prefix=answer_prefix
#         )
#
#     def get_context_data(self, **kwargs) -> Dict:
#         context = super().get_context_data(**kwargs)
#         question_formset = kwargs.get('question_formset')
#         answer_formsets = kwargs.get('answer_formsets')
#
#         if self.request.method == 'POST':
#             if question_formset is None:
#                 question_formset = self.get_question_formset(
#                     data=self.request.POST,
#                     files=self.request.FILES
#                 )
#             context['question_formset'] = question_formset
#
#             if answer_formsets is not None:
#                 for q_form, a_formset in zip(question_formset.forms, answer_formsets):
#                     q_form.answer_formset = a_formset
#             else:
#                 for q_form in question_formset:
#                     q_form.answer_formset = self._create_answer_formset(
#                         q_form,
#                         data=self.request.POST,
#                         files=self.request.FILES
#                     )
#         else:
#             if question_formset is None:
#                 question_formset = self.get_question_formset()
#             context['question_formset'] = question_formset
#
#             for q_form in question_formset:
#                 q_form.answer_formset = self._create_answer_formset(q_form)
#
#         return context
#
#     @transaction.atomic
#     def form_valid(self, form) -> HttpResponse:
#         question_formset = self.get_question_formset(
#             data=self.request.POST,
#             files=self.request.FILES
#         )
#
#         if not question_formset.is_valid():
#             return self.render_to_response(
#                 self.get_context_data(form=form, question_formset=question_formset)
#             )
#
#         all_answer_formsets: List[AnswerFormSets] = []
#         has_errors = False  # Флаг: есть ли хоть одна ошибка
#
#         for q_form in question_formset:
#             answer_formset = self._create_answer_formset(
#                 q_form,
#                 data=self.request.POST,
#                 files=self.request.FILES
#             )
#
#             # 1. Проверяем валидность formset'а
#             if not answer_formset.is_valid():
#                 has_errors = True
#
#             # 2. Проверяем логику "ровно один правильный ответ"
#             correct_count = sum(
#                 1 for f in answer_formset.forms
#                 if f.cleaned_data.get('is_correct', False)
#             )
#             if correct_count == 0:
#                 answer_formset._non_form_errors = ErrorList([
#                     "Для вопроса должен быть выбран ровно один правильный ответ."
#                 ])
#                 has_errors = True
#             elif correct_count > 1:
#                 answer_formset._non_form_errors = ErrorList([
#                     "Нельзя выбрать более одного правильного ответа."
#                 ])
#                 has_errors = True
#
#             all_answer_formsets.append(answer_formset)  # Добавляем ВСЕГДА
#
#         # 3. Если есть ошибки — возвращаем контекст со всеми formset'ами
#         if has_errors:
#             return self.render_to_response(
#                 self.get_context_data(
#                     form=form,
#                     question_formset=question_formset,
#                     answer_formsets=all_answer_formsets
#                 )
#             )
#
#         # 4. Если нет ошибок — сохраняем данные
#         try:
#             self.object = form.save()
#             questions = question_formset.save(commit=False)
#             for question in questions:
#                 question.test = self.object
#                 question.save()
#
#             for question, answer_formset in zip(questions, all_answer_formsets):
#                 answer_formset.instance = question
#                 answer_formset.save()
#
#             return super().form_valid(form)
#
#         except Exception as e:
#             messages.error(self.request, f"Ошибка сохранения: {str(e)}")
#             return self.render_to_response(
#                 self.get_context_data(
#                     form=form,
#                     question_formset=question_formset,
#                     answer_formsets=all_answer_formsets
#                 )
#             )
#
#     def form_invalid(self, form) -> HttpResponse:
#         question_formset = self.get_question_formset(
#             data=self.request.POST,
#             files=self.request.FILES
#         )
#         question_formset.is_valid()
#
#         all_answer_formsets: List[AnswerFormSets] = []
#         for q_form in question_formset:
#             answer_formset = self._create_answer_formset(
#                 q_form,
#                 data=self.request.POST,
#                 files=self.request.FILES
#             )
#             answer_formset.is_valid()  # Запускаем валидацию
#             all_answer_formsets.append(answer_formset)  # Добавляем всегда
#
#         return self.render_to_response(
#             self.get_context_data(
#                 form=form,
#                 question_formset=question_formset,
#                 answer_formsets=all_answer_formsets
#             )
#         )
#
#     def get_success_url(self) -> str:
#         return reverse("learning:program_detail", args=[self.object.program.pk])


class TestUpdateView(UpdateView):
    model = Test
    form_class = TestForm
    pk_url_kwarg = 'pk'

    # --- Создание formset для вопросов ---
    def get_question_formset(self, data: Optional[Dict] = None, files: Optional[Dict] = None):
        formset = QuestionFormSet(
            data=data,
            files=files,
            instance=self.object or self.model(),
            prefix='questions'
        )

        if data:
            total_forms = int(data.get('questions-TOTAL_FORMS', 0))
            if not hasattr(formset, '_non_form_errors') or formset._non_form_errors is None:
                formset._non_form_errors = ErrorList()

            # Проходим по всем формам, чтобы не потерять индексы
            for i in range(min(total_forms, len(formset.forms))):
                form = formset.forms[i]
                form.original_index = i
                # Просто отмечаем ошибочные формы, без удаления их
                if not form.is_valid() or not form.cleaned_data.get('text', '').strip():
                    formset._non_form_errors.append(
                        f"Вопрос {i + 1} не может быть пустым или содержит ошибки."
                    )

        return formset

    # --- Создание formset для ответов ---
    def _create_answer_formset(self, q_form, data=None, files=None):
        prefix = f'{q_form.prefix}-answers'
        return AnswerFormSets(
            data=data,
            files=files,
            instance=q_form.instance,
            prefix=prefix
        )

    # --- Добавляем формсеты в контекст ---
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        is_post = self.request.method == 'POST'

        question_formset = kwargs.get('question_formset') or self.get_question_formset(
            data=self.request.POST if is_post else None,
            files=self.request.FILES if is_post else None
        )
        context['question_formset'] = question_formset

        answer_formsets = kwargs.get('answer_formsets') or [
            self._create_answer_formset(
                q_form,
                data=self.request.POST if is_post else None,
                files=self.request.FILES if is_post else None
            )
            for q_form in question_formset.forms
        ]
        context['answer_formsets'] = answer_formsets

        # Связываем вопросы и ответы для отображения в шаблоне
        for q_form, a_formset in zip(question_formset.forms, answer_formsets):
            q_form.answer_formset = a_formset

        return context

    # --- Сохранение данных, если всё валидно ---
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
        has_errors = False

        # Валидация форм ответов для каждого вопроса
        for q_form in question_formset.forms:
            answer_formset = self._create_answer_formset(
                q_form,
                data=self.request.POST,
                files=self.request.FILES
            )

            if not answer_formset.is_valid():
                has_errors = True

            correct_count = sum(
                f.cleaned_data.get('is_correct', False)
                for f in answer_formset.forms
                if f.cleaned_data and not f.cleaned_data.get('DELETE', False)
            )

            if correct_count != 1:
                if not hasattr(answer_formset, '_non_form_errors') or answer_formset._non_form_errors is None:
                    answer_formset._non_form_errors = ErrorList()
                answer_formset._non_form_errors.append(
                    "Для вопроса должен быть выбран ровно один правильный ответ."
                )
                has_errors = True

            q_form.answer_formset = answer_formset
            all_answer_formsets.append(answer_formset)

        # Если есть ошибки, возвращаем форму с сообщениями
        if has_errors:
            return self.render_to_response(
                self.get_context_data(
                    form=form,
                    question_formset=question_formset,
                    answer_formsets=all_answer_formsets
                )
            )

        # --- Сохранение теста и связанных вопросов/ответов ---
        try:
            self.object = form.save()

            # сохраняем все вопросы, не только изменённые
            for q_form, a_formset in zip(question_formset.forms, all_answer_formsets):
                question = q_form.save(commit=False)
                question.test = self.object
                question.save()

                a_formset.instance = question
                a_formset.save()

            return super().form_valid(form)

        except Exception as e:
            messages.error(self.request, f"Ошибка сохранения: {e}")
            return self.render_to_response(
                self.get_context_data(
                    form=form,
                    question_formset=question_formset,
                    answer_formsets=all_answer_formsets
                )
            )

    # --- Если основная форма невалидна ---
    def form_invalid(self, form) -> HttpResponse:
        question_formset = self.get_question_formset(
            data=self.request.POST,
            files=self.request.FILES
        )
        all_answer_formsets = [
            self._create_answer_formset(
                q_form,
                data=self.request.POST,
                files=self.request.FILES
            )
            for q_form in question_formset.forms
        ]
        for a_formset in all_answer_formsets:
            a_formset.is_valid()

        return self.render_to_response(
            self.get_context_data(
                form=form,
                question_formset=question_formset,
                answer_formsets=all_answer_formsets
            )
        )

    def get_success_url(self):
        return reverse("learning:program_detail", args=[self.object.program.pk])
