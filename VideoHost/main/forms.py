import typing

from django import forms
import re, django.core.exceptions

from . import models
from django.core import validators


class EditUserForm(forms.ModelForm):

    class Meta:
        model = models.CustomUser
        exclude = ('created_at', 'is_staff', 'is_superuser', 'is_blocked')


# message forms:
class SendGroupMessageForm(forms.Form):

    message = forms.CharField(label='Message', widget=forms.TextInput,
    validators=[validators.MaxLengthValidator, validators.MinLengthValidator], required=False)


class EditMessageForm(forms.Form):
    edited_message = forms.CharField(label='New Message', widget=forms.TextInput, required=False, max_length=100, min_length=1,
    validators=[validators.MaxLengthValidator, validators.MinLengthValidator])



# group forms:
class CreateGroupForm(forms.ModelForm):

    group_name = forms.CharField(label='Chat Name', widget=forms.TextInput,
    validators=[validators.MaxLengthValidator], required=True)
    logo = forms.ImageField(label='Avatar', required=False,
    validators=[validators.FileExtensionValidator(allowed_extensions=('png', 'jpg', 'jpeg'))])
    members = forms.ModelChoiceField(label='Members', queryset=None, required=True)

    class Meta:
        model = models.ChatGroup
        fields = ['group_name', 'logo', 'members']

class EditGroupForm(forms.ModelForm):

    group_name = forms.CharField(label='Group Name', widget=forms.TextInput,
    validators=[validators.MaxLengthValidator, validators.MinLengthValidator], required=False)
    logo = forms.ImageField(label='Avatar', required=False,
    validators=[validators.FileExtensionValidator(allowed_extensions=('png', 'jpg', 'jpeg'))])

    class Meta:
        model = models.ChatGroup
        fields = ['group_name', 'logo']


class SongForm(forms.ModelForm):

    pass