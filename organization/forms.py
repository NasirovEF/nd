from django import forms
from organization.models import Organization, Branch, Group, District, Division


class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = "__all__"


class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = "__all__"


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = "__all__"


class DistrictForm(forms.ModelForm):
    class Meta:
        model = District
        fields = "__all__"


class DivisionForm(forms.ModelForm):
    class Meta:
        model = Division
        fields = "__all__"