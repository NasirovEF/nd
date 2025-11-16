from django import forms
from learning.models import (
    Protocol,
    Direction,
    Learner,
    Program, ProtocolResult
)
from django.forms import BooleanField, DateField
from organization.forms import StileFormMixin
from organization.models import Worker


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
        fields = "__all__"


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
