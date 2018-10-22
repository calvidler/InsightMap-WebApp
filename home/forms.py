from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm
from home.models import UserAttributes


class EditProfileForm(UserChangeForm):
    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email',
            'password',
        )


class UserInterestForm(forms.ModelForm):
    class Meta:
        model = UserAttributes
        fields = ['user', 'interests']
