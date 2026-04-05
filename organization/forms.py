from django import forms
from organization.models import (
    Organization,
    Branch,
    Group,
    District,
    Division,
    Position,
    Worker, ResponsibleForTraining,
)
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet
from django import forms


class StileFormMixin:
    # Список полей, для которых применяем ПРОСТОЙ стиль (только form-control)
    SIMPLE_FIELDS = {'organization', 'branch', 'division', 'district', 'group'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            # Сохраняем ВСЕ существующие атрибуты
            attrs = field.widget.attrs.copy()  # копируем, чтобы не менять оригинал напрямую
            current_classes = attrs.get('class', '').split()

            if isinstance(field, forms.BooleanField):
                attrs['class'] = 'form-check-input'
                field.widget.attrs.update(attrs)  # обновляем, сохраняя required и др.

            elif isinstance(field, forms.DateField):
                field.widget = forms.DateInput(
                    attrs={
                        'class': 'form-control',
                        'type': 'date'
                    }
                )

            elif isinstance(field, forms.ModelChoiceField):
                if field_name in self.SIMPLE_FIELDS:
                    updated_classes = set(current_classes) | {'form-control'}
                    attrs['class'] = ' '.join(updated_classes)
                else:
                    select_classes = {'form-control', 'form-select', 'selectpicker'}
                    updated_classes = set(current_classes) | select_classes
                    attrs.update({
                        'class': ' '.join(updated_classes),
                        'data-live-search': 'true',
                        'title': 'Выберите вариант',
                        'style': 'max-width: 400px;',
                    })
                field.widget.attrs.update(attrs)

            elif isinstance(field, forms.ModelMultipleChoiceField):
                if field_name in self.SIMPLE_FIELDS:
                    updated_classes = set(current_classes) | {'form-control'}
                    attrs['class'] = ' '.join(updated_classes)
                else:
                    select_classes = {'form-control', 'form-select', 'selectpicker'}
                    updated_classes = set(current_classes) | select_classes
                    attrs.update({
                        'class': ' '.join(updated_classes),
                        'data-live-search': 'true',
                        'multiple': 'multiple',
                        'title': 'Выберите варианты',
                        'style': 'max-width: 400px;',
                    })
                field.widget.attrs.update(attrs)
            else:
                updated_classes = set(current_classes) | {'form-control'}
                attrs['class'] = ' '.join(updated_classes)
                field.widget.attrs.update(attrs)


class OrganizationForm(StileFormMixin, forms.ModelForm):
    class Meta:
        model = Organization
        fields = "__all__"


class BranchForm(StileFormMixin, forms.ModelForm):
    class Meta:
        model = Branch
        exclude = ["organization"]


class GroupForm(StileFormMixin, forms.ModelForm):
    class Meta:
        model = Group
        exclude = ["district"]


class DistrictForm(StileFormMixin, forms.ModelForm):
    class Meta:
        model = District
        exclude = ["division"]


class DivisionForm(StileFormMixin, forms.ModelForm):
    class Meta:
        model = Division
        exclude = ["branch"]


class PositionForm(StileFormMixin, forms.ModelForm):
    class Meta:
        model = Position
        fields = ["name", "is_main"]


class WorkerCreateForm(StileFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['organization'].queryset = Organization.objects.filter(is_main=True)

    class Meta:
        model = Worker
        exclude = ["image", "dismissed"]


class WorkerUpdateForm(WorkerCreateForm):
    class Meta:
        model = Worker
        exclude = ["image"]


class ResponsibleForTrainingForm(StileFormMixin, forms.ModelForm):
    class Meta:
        model = ResponsibleForTraining
        fields = "__all__"


class PositionFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()

        if any(self.errors):
            return

        main_count = 0
        for form in self.forms:
            if self._should_delete_form(form):
                continue

            if form.cleaned_data.get("is_main"):
                main_count += 1

        if main_count == 0:
            raise ValidationError("У работника должна быть основная профессия")
        if main_count > 1:
            raise ValidationError("У работника может быть только одна основная профессия")
