from django import forms
from accident.models import Accident
from organization.forms import StileFormMixin


class AccidentForm(StileFormMixin, forms.ModelForm):
    class Meta:
        model = Accident
        fields = "__all__"
