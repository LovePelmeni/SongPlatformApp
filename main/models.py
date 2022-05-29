from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin

from django.db import models
import typing, requests, json

from .aws_s3 import exceptions
import django.dispatch
from django import db

user_created = django.dispatch.dispatcher.Signal()
user_deleted = django.dispatch.dispatcher.Signal()



class PhoneNumberField(models.CharField):

    def __init__(self, **kwargs):
        self.max_length = kwargs.get('max_length')
        super(PhoneNumberField, self).__init__(**kwargs)

    def db_type(self, connection):
        return 'char(%s)' % 100

    def to_python(self, value):
        return value


class CustomManager(BaseUserManager):

    def create_user(self, **kwargs):
        user = self.model(**kwargs)
        user.set_password(raw_password=kwargs.get('password'))
        user.save(using=self._db)
        user_created.send(sender=self, user=user)
        return user

    def create_superuser(self, username, password, phone_number):
        user = self.model(username=username, password=password, phone_number=phone_number, is_staff=True)
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):

    objects = CustomManager()

    username = models.CharField(verbose_name='Username', max_length=100, unique=True)
    phone_number = PhoneNumberField(verbose_name='Phone Number', max_length=100, null=False)

    avatar_image = models.URLField(verbose_name='User Avatar', null=True, max_length=100)

    email = models.EmailField(verbose_name='Email', null=True, max_length=100)
    password = models.CharField(verbose_name='Password', null=False, max_length=100)

    created_at = models.DateTimeField(verbose_name='User Created At', auto_now=True)
    is_superuser = models.BooleanField(verbose_name='Is Authenticated', default=True)

    is_staff = models.BooleanField(verbose_name='Is Staff', default=False)
    is_blocked = models.BooleanField(verbose_name='is_blocked', default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['password', 'phone_number']

    class Meta:
        indexes = [
            models.Index(fields=['created_at'], name='created_at_index')
        ]

    def __str__(self):
        return self.username

    def apply_new_avatar(self, avatar):

        from . import aws_s3
        bucket_name = settings.AWS_IMAGE_BUCKET_NAME
        aws_s3.files_api._delete_from_aws_storage(bucket_name=bucket_name,
        file_link=self.avatar_image)

        avatar_url = aws_s3.files_api._save_file_to_aws(bucket_name=bucket_name,
        file=avatar)
        self.avatar_image = avatar_url
        self.save(using=self._db)


    def delete(self, using=typing.Literal["default"], **kwargs):
        try:
            user_deleted.send(sender=self, user=user)
            return super().delete(using=using, **kwargs)

        except() as exception:
            logger.debug('could not create user xmpp profile: [%s]' % exception)
            raise exceptions.XMPPUserDeleteFailed()



from django.conf import settings
class SongManager(models.Manager):

    def create(self, **kwargs):
        model = self.model(**kwargs)
        return model

class Subscription(pydantic.BaseModel):

    subscription_id: int
    subscription_name: str
    amount: str

class Song(models.Model):

    objects = SongManager()
    subscription: typing.Optional[Subscription]

    owner = models.ManyToManyField(CustomUser, related_name='songs')
    preview = models.CharField(verbose_name='AWS Preview File link', max_length=100, null=True)
    song_name = models.CharField(verbose_name='Song Name', null=False, max_length=100)
    song_description = models.TextField(verbose_name='Song Description', null=True, max_length=100)
    audio_file = models.CharField(verbose_name='AWS Audio File Link', null=False, max_length=300)

    def delete(self, using=None, **kwargs):
        from . import aws_s3
        aws_s3.files_api._delete_from_aws_storage(file_link=kwargs.get('file_link'))
        return super().delete(using=using, **kwargs)



