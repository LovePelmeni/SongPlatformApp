from rest_framework import serializers
from . import models

from django.core import validators

class PhoneNumberField(serializers.CharField):

    def __init__(self, **kwargs):
        super(PhoneNumberField, self).__init__(**kwargs)
        self.error_messages = {"required": 'Phone Number field is required'}
        self.regexs = ["(^8|7|\+7)((\d{10})|(\s\(\d{3}\)\s\d{3}\s\d{2}\s\d{2}))"] # list of phone numbers regular expressions

    def validate(self, value):
        for regex in regexes:
            if re.match(pattern=regex, string=value):
                return value.replace('+7', '8')
            continue
        raise django.core.exceptions.ValidationError(message='invalid phone number')


class UserSerializer(serializers.ModelSerializer):


    avatar_image = serializers.ImageField(label='Image',
    validators=[validators.FileExtensionValidator(
    allowed_extensions=('png', 'jpeg', 'jpg'))], required=False)

    email = serializers.EmailField(label='Email', validators=[validators.EmailValidator], required=True)
    username = serializers.CharField(label='Username',
    validators=[validators.MaxLengthValidator], required=True)

    phone_number = PhoneNumberField(label='Phone Number',
    validators=[validators.MaxLengthValidator, validators.MinLengthValidator], max_length=12, required=True)

    password = serializers.CharField(label='Password',  validators=[validators.MaxLengthValidator,
    validators.MinLengthValidator], required=True)

    class Meta:
        model = models.CustomUser
        fields = ['avatar_image', 'email', 'username', 'phone_number', 'password']

    def validate_username(self, value):
        if not value in models.CustomUser.objects.values_list('username'):
            return value
        raise django.core.exceptions.ValidationError('User with this name is already exists.')


class UserLoginSerializer(UserSerializer):

    def __init__(self, *args, **kwargs):
        super(UserSerializer, self).__init__(*args, **kwargs)
        del self.fields['phone_number']
        del self.fields['avatar_image']


class SongsSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Song
        exclude = ('song_name', 'amount', 'owners')

class SongSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Song
        fields = '__all__'

class SongCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Song
        fields = "__all__"


