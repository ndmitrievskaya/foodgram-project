from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import password_validation


class SignUpForm(UserCreationForm):
    name = forms.CharField(max_length=100, help_text='First Name', label='Имя пользователя')
    email = forms.EmailField(max_length=150, help_text='Email', label='Адрес электронной почты')
    password1 = forms.CharField(max_length=100, strip=False, widget=forms.PasswordInput, label='Пароль',
                                help_text=password_validation.password_validators_help_text_html())
    password2 = None

    class Meta:
        model = User
        exclude = ('last_name',)
        fields = ('username', 'name',
                  'email',)
        labels = {
            'username': _('Имя'),
        }


class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("first_name", "last_name", "username", "email")
