from django import forms
from learning.models import (
    Protocol,
    Direction,
    Learner,
    Program, ProtocolResult, Question, Answer, Test, ProgramBriefing, BriefingDay
)
from datetime import timedelta
from django.forms import BaseInlineFormSet
from django.core.exceptions import ValidationError
from learning.models.learner_direction import LearningDoc, LearningPoster
from organization.forms import StileFormMixin


class ProtocolUpdateForm(StileFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['program'].queryset = Program.objects.filter(is_active=True)

    class Meta:
        model = Protocol
        fields = "__all__"
        widgets = {
            'division': forms.Select(
                attrs={'class': 'form-control form-select selectpicker', 'data-live-search': 'true',
                       'title': 'Выберите структурное подразделение...'}),
            'chairman': forms.Select(attrs={'class': 'form-control form-select selectpicker', 'data-live-search': 'true', 'title': 'Выберите председателя комиссии...'}),
            'members': forms.SelectMultiple(attrs={'class': 'form-control form-select selectpicker', 'data-live-search': 'true', 'title': 'Выберите членов комиссии...'}),
            'prot_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'program': forms.SelectMultiple(attrs={'class': 'form-control form-select selectpicker', 'data-live-search': 'true', 'title': 'Выберите программы обучения...'}),
            'learner': forms.SelectMultiple(attrs={'class': 'form-control form-select selectpicker', 'data-live-search': 'true', 'title': 'Выберите работников...'}),
            'doc_scan': forms.ClearableFileInput(attrs={'class': 'form-control', 'aria-label': 'Загрузка файла'}),
        }

    def clean(self):
        errors = []
        cleaned_data = super().clean()
        learners = cleaned_data.get("learner")
        programs = cleaned_data.get("program")
        if learners and programs:
            for learner in learners:
                learner_direction = learner.direction.all()
                for program in programs:
                    for direction in program.direction.all():
                        if direction not in learner_direction:
                            errors.append(f"Работнику ({learner}) не требуется обучение по направлению: {direction}")
        if errors:
            raise forms.ValidationError(errors)
        return cleaned_data


class ProtocolCreateForm(ProtocolUpdateForm):
    class Meta(ProtocolUpdateForm.Meta):
        model = Protocol
        exclude = ["doc_scan"]


class DirectionForm(StileFormMixin, forms.ModelForm):
    class Meta:
        model = Direction
        fields = "__all__"


class LearnerForm(StileFormMixin, forms.ModelForm):
    class Meta:
        model = Learner
        fields = ["direction"]


class ProgramForm(StileFormMixin, forms.ModelForm):
    error_css_class = 'text-danger'

    def clean(self):
        cleaned_data = super().clean()
        replacement = cleaned_data.get('replacement')
        if replacement:
            if self.instance.pk and replacement.pk == self.instance.pk:
                self.add_error(
                    'replacement',
                    "Программа не может заменять саму себя."
                )

        subdirection = cleaned_data.get('subdirection')
        direction = cleaned_data.get('direction')
        if direction.filter(have_sub_direction=True) and not subdirection:
            self.add_error(
                'direction',
                "Выберите поднаправления обучения 'В'"
            )
        if subdirection and subdirection.exists():
            if not direction.filter(have_sub_direction=True).exists():
                self.add_error(
                    'direction',
                    "Выберите направление обучения 'В' или уберите поднаправления"
                )

        return cleaned_data

    class Meta:
        model = Program
        exclude = ["is_active"]


class ProgramFormNotActive(ProgramForm):
    class Meta:
        model = Program
        exclude = ["replacement", "is_active"]


class ProtocolResultForm(StileFormMixin, forms.ModelForm):
    passed = forms.BooleanField(required=False, label='Сдал')
    comment = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 2}),
        label='Комментарий'
    )

    def clean(self):
        cleaned_data = super().clean()
        learner = cleaned_data.get('learner')
        passed = cleaned_data.get('passed')
        protocol = cleaned_data.get('protocol')

        if not learner or not protocol:
            return cleaned_data

        if passed is not True:
            return cleaned_data

        programs = protocol.program.all()
        if not programs:
            raise ValidationError('У протокола нет связанных программ.')

        program_ids = [p.id for p in programs]
        start_date = protocol.prot_date - timedelta(days=60)

        # 1. Ищем несданные экзамены
        failed_exams = learner.exam_results.filter(
            exam__program__in=program_ids,
            is_passed=False,
            test_date__gte=start_date,
            test_date__lte=protocol.prot_date
        )

        # 2. Ищем сданные экзамены
        passed_exams = learner.exam_results.filter(
            exam__program__in=program_ids,
            is_passed=True,
            test_date__gte=start_date,
            test_date__lte=protocol.prot_date
        )

        # 3. Собираем ID программ, по которым есть результаты
        covered_program_ids = set(passed_exams.values_list('exam__program_id', flat=True))
        covered_program_ids.update(
            failed_exams.values_list('exam__program_id', flat=True)
        )

        # 4. Проверяем, все ли программы покрыты
        missing_programs = [
            p for p in programs
            if p.id not in covered_program_ids
        ]

        # 5. Формируем ошибки
        errors = []

        if failed_exams.exists():
            failed_programs = failed_exams.values_list(
                'exam__program__name', flat=True
            ).distinct()
            errors.append(
                f'Работник не сдал тест по программам: {", ".join(failed_programs)}.'
            )

        if missing_programs:
            missing_names = [p.name for p in missing_programs]
            errors.append(
                f'Нет результатов тестирования по программам: {", ".join(missing_names)}.'
            )

        if errors:
            # Объединяем все ошибки
            raise ValidationError('. '.join(errors) + ' Отметка "Сдал" невозможна.')

        return cleaned_data

    class Meta:
        model = ProtocolResult
        fields = ['id', 'protocol', 'learner', 'passed', 'comment']


class TestForm(StileFormMixin, forms.ModelForm):
    class Meta:
        model = Test
        fields = []


class AnswerForm(forms.ModelForm):
    is_correct = forms.BooleanField(
        required=False,
        label="Правильный ответ"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['text'].widget.attrs.pop('required', None)


    class Meta:
        model = Answer
        fields = ['id', 'text', 'is_correct']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'style': 'height: 60px;',
                'placeholder': 'Введите текст ответа'
            })
        }
        field_options = {
            'text': {'strip': True}
        }

    def clean(self):
        cleaned_data = super().clean()
        text = cleaned_data.get('text', '').strip()
        is_correct = cleaned_data.get('is_correct')

        # 1. Текст обязателен для всех ответов
        if not text:
            self.add_error('text', "Текст ответа не может быть пустым.")
        # 2. Для правильного ответа текст уже проверен выше
        return cleaned_data



class QuestionForm(forms.ModelForm):
    text = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'style': 'height: 80px;',
            'placeholder': 'Введите текст вопроса'
        }),
        required=True,  # Явно указываем обязательность
        strip=True
    )

    def clean_text(self):
        text = self.cleaned_data.get('text')
        if text and not text.strip():
            raise forms.ValidationError('Текст вопроса не может быть пустым.')
        return text

    class Meta:
        model = Question
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'style': 'height: 80px;',
                'placeholder': 'Введите текст вопроса'
            })
        }


class QuestionFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()

        for i, form in enumerate(self.forms):
            # Пропускаем удалённые вопросы
            if form.cleaned_data and form.cleaned_data.get('DELETE'):
                continue

            # Для существующих вопросов: проверяем ответы
            if form.instance.pk:
                self._validate_question_answers(form)

            # Для новых вопросов (extra): проверяем, что пользователь начал заполнять ответы
            elif form.has_changed():
                self._validate_question_answers(form, is_new=True)

    def _validate_question_answers(self, question_form, is_new=False):
        # Получаем формсет ответов для этого вопроса
        answer_formset = question_form.answer_formset

        # Собираем валидные формы ответов (не удалённые и не пустые)
        valid_answers = []
        for ans_form in answer_formset.forms:
            if ans_form.cleaned_data and ans_form.cleaned_data.get('DELETE'):
                continue  # Пропускаем удалённые

            text = ans_form.cleaned_data.get('text', '').strip()
            if text:  # Только непустые ответы
                valid_answers.append(ans_form)

        # Проверка 1: должно быть ровно 3 ответа
        if len(valid_answers) != 3:
            msg = "Для вопроса должно быть ровно 3 варианта ответа."
            if is_new:
                msg += " Заполните все 3 поля."
            question_form.add_error(None, msg)

        # Проверка 2: ровно один правильный ответ
        correct_count = sum(1 for f in valid_answers if f.cleaned_data.get('is_correct', False))
        if correct_count != 1:
            question_form.add_error(
                None,
                "Для вопроса должен быть выбран ровно один правильный ответ."
            )


class AnswerFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()

        validanswers = []
        empty_text_errors = []

        for i, form in enumerate(self.forms):
            if form.cleaned_data and form.cleaned_data.get('DELETE'):
                continue

            text = form.cleaned_data.get('text', '').strip()
            if not text:
                empty_text_errors.append(f"Ответ {i+1}: текст не может быть пустым.")
            else:
                validanswers.append(form)


        if empty_text_errors:
            raise ValidationError(empty_text_errors)

        if len(validanswers) != 3:
            raise ValidationError("Для вопроса должно быть ровно 3 варианта ответа.")

        correct_count = sum(1 for f in validanswers if f.cleaned_data.get('is_correct', False))
        if correct_count != 1:
            raise ValidationError("Для вопроса должен быть выбран ровно один правильный ответ.")


# Формсеты
QuestionFormSets = forms.inlineformset_factory(
    Test,
    Question,
    form=QuestionForm,
    formset=QuestionFormSet,
    extra=1,
    max_num=100,
    can_delete=True,
    validate_max=False,
    validate_min=False,
)

AnswerFormSets = forms.inlineformset_factory(
    Question,
    Answer,
    form=AnswerForm,
    formset=AnswerFormSet,
    extra=0,  # Важно: extra=0, чтобы не было пустых полей
    max_num=3,
    min_num=3,  # Обязательно 3 формы
    validate_min=True,
    validate_max=True,
    can_delete=False,
)


class LearningDocForm(StileFormMixin, forms.ModelForm):
    # Скрытое поле для хранения ID связанного объекта
    object_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = LearningDoc
        fields = ['name', 'doc', 'object_id']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Если есть instance, заполняем object_id
        if self.instance and self.instance.pk:
            self.fields['object_id'].initial = self.instance.object_id


class LearningPosterForm(StileFormMixin, forms.ModelForm):
    object_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = LearningPoster
        fields = ['name', 'image', 'object_id']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['object_id'].initial = self.instance.object_id


class ProgramBriefingForm(StileFormMixin, forms.ModelForm):
    error_css_class = 'text-danger'

    def clean(self):
        cleaned_data = super().clean()
        replacement = cleaned_data.get('replacement')
        if replacement:
            if self.instance.pk and replacement.pk == self.instance.pk:
                self.add_error(
                    'replacement',
                    "Программа не может заменять саму себя."
                )

        return cleaned_data

    class Meta:
        model = ProgramBriefing
        exclude = ["is_active"]


class ProgramBriefingNotActive(ProgramBriefingForm):
    class Meta:
        model = ProgramBriefing
        exclude = ["replacement", "is_active"]


class BriefingDayForm(StileFormMixin, forms.ModelForm):
    class Meta:
        model = BriefingDay
        exclude = ["learner", "next_briefing_day", "is_active"]
