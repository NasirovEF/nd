from django import forms
from learning.models import (
    Protocol,
    Direction,
    Learner,
    Program
)
from django.forms import BooleanField, DateField
from organization.forms import StileFormMixin


class ProtocolForm(StileFormMixin, forms.ModelForm):
    class Meta:
        model = Protocol
        fields = "__all__"


class DirectionForm(StileFormMixin, forms.ModelForm):
    class Meta:
        model = Direction
        fields = "__all__"


class LearnerForm(StileFormMixin, forms.ModelForm):
    class Meta:
        model = Learner
        fields = "__all__"


class ProgramForm(StileFormMixin, forms.ModelForm):
    class Meta:
        model = Program
        fields = "__all__"
