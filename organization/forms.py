from django import forms
from organization.models import (
    Organization,
    Branch,
    Group,
    District,
    Division,
    Position,
    Worker,
)
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory, BaseInlineFormSet
from django.forms import BooleanField, DateField, SelectMultiple


class StileFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            # Получаем текущие классы виджета (если есть)
            current_classes = field.widget.attrs.get('class', '')

            if isinstance(field, BooleanField):
                # Для чекбоксов
                field.widget.attrs['class'] = 'form-check-input'
            elif isinstance(field, DateField):
                # Для дат
                field.widget.attrs['class'] = f'{current_classes} form-control'.strip()
                field.widget.attrs['type'] = 'date'
            elif isinstance(field, SelectMultiple):
                # Для множественного выбора — добавляем классы к существующим
                new_classes = f'{current_classes} form-control form-select selectpicker'.strip()
                field.widget.attrs['class'] = new_classes
            else:
                # Для остальных полей
                new_classes = f'{current_classes} form-control'.strip()
                field.widget.attrs['class'] = new_classes


class OrganizationForm(StileFormMixin, forms.ModelForm):
    class Meta:
        model = Organization
        fields = "__all__"


class BranchForm(StileFormMixin, forms.ModelForm):
    class Meta:
        model = Branch
        fields = ["name"]


class GroupForm(StileFormMixin, forms.ModelForm):
    class Meta:
        model = Group
        fields = ["name"]


class DistrictForm(StileFormMixin, forms.ModelForm):
    class Meta:
        model = District
        fields = ["name"]


class DivisionForm(StileFormMixin, forms.ModelForm):
    class Meta:
        model = Division
        fields = ["name"]


class PositionForm(StileFormMixin, forms.ModelForm):
    class Meta:
        model = Position
        fields = ["name", "is_main"]


class WorkerCreateForm(StileFormMixin, forms.ModelForm):
    class Meta:
        model = Worker
        fields = ["surname", "name", "patronymic"]


class WorkerUpdateForm(StileFormMixin, forms.ModelForm):
    class Meta:
        model = Worker
        fields = ["surname", "name", "patronymic", "dismissed"]


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
