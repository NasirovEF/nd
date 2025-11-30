from django.views.generic import CreateView
from django.shortcuts import reverse
from django.contrib import messages
from django.forms.utils import ErrorList
from learning.models import Test, Question, Answer
from learning.forms import TestForm, QuestionFormSet, AnswerFormSets


class TestCreateView(CreateView):
    model = Test
    form_class = TestForm

    def get_question_formset(self, data=None, files=None):
        formset = QuestionFormSet(
            data=data,
            files=files,
            instance=self.object or Test(),
            prefix='questions'
        )

        # Фильтруем формы, для которых есть данные в POST
        if data:
            total_forms = int(data.get('questions-TOTAL_FORMS', 0))
            valid_forms = []
            for i in range(total_forms):
                text_key = f'questions-{i}-text'
                if text_key in data:  # Есть данные для этого вопроса?
                    valid_forms.append(formset.forms[i])
            formset.forms = valid_forms
            formset._total_form_count = len(valid_forms)

        return formset

    def get_answer_formset(self, question_instance, data=None, files=None, prefix=None):
        return AnswerFormSets(
            data=data,
            files=files,
            instance=question_instance,
            prefix=prefix
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if 'answer_formsets' in kwargs:
            context['question_formset'] = self.get_question_formset(
                data=self.request.POST,
                files=self.request.FILES
            )

            # Явно проверяем валидность question_formset
            if self.request.method == 'POST':
                context['question_formset'].is_valid()

            for q_form in context['question_formset']:
                idx = context['question_formset'].forms.index(q_form)
                answer_prefix = f'questions-{idx}-answers'

                q_form.answer_formset = self.get_answer_formset(
                    question_instance=q_form.instance if q_form.instance.pk else None,
                    data=self.request.POST,
                    files=self.request.FILES,
                    prefix=answer_prefix
                )

                # Явно запускаем валидацию для answer_formset
                if self.request.method == 'POST':
                    q_form.answer_formset.is_valid()
        else:
            # Инициализация для GET
            context['question_formset'] = self.get_question_formset()
            for q_form in context['question_formset']:
                q_form.answer_formset = self.get_answer_formset(
                    question_instance=q_form.instance,
                    prefix=f'{q_form.prefix}-answers'
                )

        return context

    def form_valid(self, form):
        print("=== POST KEYS ===")
        for key in self.request.POST:
            print(key)

        question_formset = self.get_question_formset(
            data=self.request.POST,
            files=self.request.FILES
        )

        if not question_formset.is_valid():
            return self.render_to_response(
                self.get_context_data(form=form, question_formset=question_formset)
            )

        all_answer_formsets = []
        for q_form in question_formset:
            answer_prefix = f'{q_form.prefix}-answers'
            answer_formset = self.get_answer_formset(
                question_instance=q_form.instance,
                data=self.request.POST,
                files=self.request.FILES,
                prefix=answer_prefix
            )

            # Запускаем валидацию
            if not answer_formset.is_valid():
                all_answer_formsets.append(answer_formset)
                return self.render_to_response(
                    self.get_context_data(
                        form=form,
                        question_formset=question_formset,
                        **{'answer_formsets': all_answer_formsets}
                    )
                )

            # Если валидация прошла, но нужны дополнительные проверки
            correct_count = sum(
                1 for f in answer_formset.forms
                if f.cleaned_data.get('is_correct', False)
            )

            if correct_count == 0:
                from django.forms.utils import ErrorList
                answer_formset._non_form_errors = ErrorList([
                    "Для вопроса должен быть выбран ровно один правильный ответ."
                ])
                all_answer_formsets.append(answer_formset)
                return self.render_to_response(
                    self.get_context_data(
                        form=form,
                        question_formset=question_formset,
                        **{'answer_formsets': all_answer_formsets}
                    )
                )
            elif correct_count > 1:
                from django.forms.utils import ErrorList
                answer_formset._non_form_errors = ErrorList([
                    "Нельзя выбрать более одного правильного ответа."
                ])
                all_answer_formsets.append(answer_formset)
                return self.render_to_response(
                    self.get_context_data(
                        form=form,
                        question_formset=question_formset,
                        **{'answer_formsets': all_answer_formsets}
                    )
                )

            all_answer_formsets.append(answer_formset)

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
                    **{'answer_formsets': all_answer_formsets}
                )
            )

    def form_invalid(self, form):
        # Пересоздаём question_formset из POST-данных
        question_formset = self.get_question_formset(
            data=self.request.POST,
            files=self.request.FILES
        )
        # Запускаем валидацию, чтобы заполнить .errors
        question_formset.is_valid()

        # Собираем все answer_formset для каждого вопроса
        all_answer_formsets = []
        for q_form in question_formset:
            answer_prefix = f'{q_form.prefix}-answers'
            answer_formset = self.get_answer_formset(
                question_instance=q_form.instance if q_form.instance.pk else None,
                data=self.request.POST,
                files=self.request.FILES,
                prefix=answer_prefix
            )
            # Запускаем валидацию для набора ответов
            answer_formset.is_valid()
            all_answer_formsets.append(answer_formset)

        # Возвращаем ответ с полным контекстом
        return self.render_to_response(
            self.get_context_data(
                form=form,
                question_formset=question_formset,
                **{'answer_formsets': all_answer_formsets}  # Явно передаём в контекст
            )
        )

    def get_success_url(self):
        return reverse("organization:organization_list")
