from organization.forms import StileFormMixin
from users.models import User
from  django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.contrib.auth.forms import UserChangeForm


class UserLoginViewForm(StileFormMixin, AuthenticationForm):
    model = User
    fields = ("service_number", "password")


class AdminPasswordChangeForm(forms.Form):
    password1 = forms.CharField(
        label="Новый пароль",
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        required=False,
    )
    password2 = forms.CharField(
        label="Подтверждение пароля",
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        required=False,
    )

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if not password1 and not password2:
            return cleaned_data  # Ничего не вводили — пропускаем

        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError("Пароли не совпадают.")
        else:
            raise forms.ValidationError("Введите и подтвердите новый пароль.")
        return cleaned_data

    def save(self, commit=True):
        user = self.instance
        if self.cleaned_data["password1"]:
            user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
