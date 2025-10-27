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
from django.forms import BooleanField, DateField


class StileFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field, BooleanField):
                field.widget.attrs["class"] = "form-check-input"
            elif isinstance(field, DateField):
                field.widget.attrs["class"] = "form-control"
                field.widget.attrs["type"] = "date"
            else:
                field.widget.attrs["class"] = "form-control"

class OrganizationForm(StileFormMixin, forms.ModelForm):
    class Meta:
        model = Organization
        fields = "__all__"


class BranchForm(StileFormMixin, forms.ModelForm):
    class Meta:
        model = Branch
        fields = "__all__"


class GroupForm(StileFormMixin, forms.ModelForm):
    class Meta:
        model = Group
        fields = "__all__"


class DistrictForm(StileFormMixin, forms.ModelForm):
    class Meta:
        model = District
        fields = "__all__"


class DivisionForm(StileFormMixin, forms.ModelForm):
    class Meta:
        model = Division
        fields = "__all__"


class PositionForm(StileFormMixin, forms.ModelForm):
    class Meta:
        model = Position
        fields = "__all__"


class WorkerForm(StileFormMixin, forms.ModelForm):
    class Meta:
        model = Worker
        fields = "__all__"
