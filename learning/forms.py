from django import forms
from learning.models import (
    Protocol,
    Direction,
    Learner,
    Program, ProtocolResult, Question, Answer, Test
)
from django.forms import BaseInlineFormSet
from organization.forms import StileFormMixin


class ProtocolUpdateForm(StileFormMixin, forms.ModelForm):
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
            'direction': forms.SelectMultiple(attrs={'class': 'form-control form-select selectpicker', 'data-live-search': 'true', 'title': 'Выберите направление обучения...'}),
            'doc_scan': forms.ClearableFileInput(attrs={'class': 'form-control', 'aria-label': 'Загрузка файла'}),
        }

    def clean(self):
        errors = []
        cleaned_data = super().clean()
        learners = cleaned_data.get("learner")
        directions = cleaned_data.get("direction")
        if learners and directions:
            for learner in learners:
                learner_direction = learner.direction.all()
                for direction in directions:
                    if direction not in learner_direction:
                        errors.append(f"{learner} не требуется обучение по {direction}")
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
    class Meta:
        model = Program
        exclude = ["is_active"]


class ProtocolResultForm(StileFormMixin, forms.ModelForm):
    passed = forms.BooleanField(required=False, label='Сдал')
    comment = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 2}),
        label='Комментарий'
    )

    class Meta:
        model = ProtocolResult
        fields = ['id', 'passed', 'comment']


class TestForm(StileFormMixin, forms.ModelForm):
    class Meta:
        model = Test
        fields = ['program']


class AnswerForm(forms.ModelForm):
    is_correct = forms.BooleanField(
        required=False,
        label="Правильный ответ"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['text'].widget.attrs.update({'required': True})


    class Meta:
        model = Answer
        fields = ['text', 'is_correct']
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
        is_correct = cleaned_data.get('is_correct')
        text = cleaned_data.get('text')


        if is_correct and (not text or text.strip() == ''):
            self.add_error('text', "Нельзя отметить ответ как правильный, если текст ответа пуст.")


        return cleaned_data



class QuestionForm(forms.ModelForm):
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


class AnswerFormSet(BaseInlineFormSet):
    def add_fields(self, form, index):
        super().add_fields(form, index)
        form.auto_id = f'answer-{self.instance.id or "new"}-{index}'


# Формсеты
QuestionFormSet = forms.inlineformset_factory(
    Test,
    Question,
    form=QuestionForm,
    extra=3,
    can_delete=True,
    # Важно: не пропускать пустые формы при валидации
    validate_max=False,
    validate_min=False,
)

AnswerFormSets = forms.inlineformset_factory(
    Question,
    Answer,
    form=AnswerForm,
    formset=AnswerFormSet,
    extra=3,
    can_delete=False,
    validate_max=False,
    validate_min=False,
)
