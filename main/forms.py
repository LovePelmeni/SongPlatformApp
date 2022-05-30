import typing

from django import forms
import re, django.core.exceptions

from . import models
from django.core import validators


class EditUserForm(forms.ModelForm):

    class Meta:
        model = models.CustomUser
        exclude = ('created_at', 'is_staff', 'is_superuser', 'is_blocked')


class SongForm(forms.ModelForm):

    preview = forms.ImageField(label='Preview', validators=[validators.FileExtensionValidator(
    allowed_extensions=('.png', '.jpg', '.jpeg'))], required=False)
    song_name = forms.CharField(label='Song Name', required=True,
    validators=[validators.MaxLengthValidator, validators.MinLengthValidator])
    song_description = forms.CharField(label='Song Description', required=True)
    audio_file = forms.FileField(label='Audio File', required=True,
    validators=[validators.FileExtensionValidator(allowed_extensions=('.wav', '.mp4', '.aac', '.mp3'))])

    class Meta:
        model = models.Song
        fields = ('preview', 'song_name', 'song_description', 'audio_file')

