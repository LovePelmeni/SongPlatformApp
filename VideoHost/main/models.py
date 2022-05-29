import django.http
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin

from django.db import models, transaction
from django.conf import settings
import typing, requests, json

from . import exceptions
import django.dispatch
from django import db


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
        try:
            import requests
            user = self.model(**kwargs)
            user.set_password(raw_password=kwargs.get('password'))
            user.save(using=self._db)

            response = requests.post(url='http://localhost:8090/create/xmpp/client/', data={'user_id': user.id})
            response.raise_for_status()
            user.__setattr__('xmpp_jid', json.loads(response.text)['jid_username'])
            user.__setattr__('xmpp_password', json.loads(response.text)['jid_password'])
            return user

        except() as exception:
            logger.debug('could not create xmpp profile: %s' % exception)
            raise exceptions.XMPPUserCreationFailed()

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
            response = requests.delete('http://localhost:8090/delete/xmpp/client/', params={'user_id': self.id})
            response.raise_for_status()
            return super().delete(using=using, **kwargs)

        except() as exception:
            logger.debug('could not create user xmpp profile: [%s]' % exception)
            raise exceptions.XMPPUserDeleteFailed()


class Video(models.Model):

    objects = models.Manager()

    name = models.CharField(verbose_name='Video Name', unique=True, max_length=30)
    file_link = models.CharField('File AWS Key Link', max_length=100)
    created_at = models.DateTimeField(verbose_name='Created At', auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        indexes = [
            db.models.Index(fields=['created_at'], name='video_created_at_pkey')
        ]

from django.contrib.auth import get_user_model
from django.conf import settings


class ChatManager(django.db.models.Manager):
    """
    Class for handles different states of the Chat Model Class.
    Basically used for handling create/delete states and apply changes to XMPP Server Group Chats.
    """

    def create(self, using=None, *args, **kwargs):
        try:
            import django.middleware.csrf, requests
            new_object = ChatGroup(*args, **kwargs).save(using=self.db)
            response = requests.post('http://localhost:8090/create/group/',
            params={'group_id': new_object.id, 'owner_jid': kwargs.get('owner_jid')})
            response.raise_for_status()
            return new_object

        except() as exception:
            logger.debug('could not create user xmpp profile: [%s]' % exception)
            raise exceptions.XMPPGroupCreationFailed()


class ChatGroup(models.Model):
    """
    Base Model for Group Chat.
    """

    objects = ChatManager()

    logo = models.CharField(verbose_name='Group Avatar Link', null=True, default=
    getattr(settings, 'MEDIA_ROOT') + '/default.png', max_length=300)
    group_name = models.CharField(verbose_name='Group Name', max_length=20)

    videos = models.ForeignKey(verbose_name='Group Videos', to=Video, on_delete=models.PROTECT)
    members = models.ManyToManyField(verbose_name='Group Members', to=CustomUser, related_name='chat_groups')
    last_updated = models.DateTimeField(verbose_name='Last Updated')

    class Meta:
        verbose_name = 'Group Chat'
        verbose_name_plural = 'Group Chats'

    def __str__(self):
        return self.group_name

    def get_default_avatar_url(self):
        return getattr(settings, 'MEDIA_ROOT') + '/default.png'

    def get_last_updated(self):
        return self.last_updated

    def get_members_count(self):
        return self.members.count()

    def generate_etag(self):
        return 'etag-%s-%s-%s' % (self.id, self.group_name,
        datetime.datetime.now().strftime('%H-%d-%y'))

    def apply_new_etag(self):
        self.etag = generate_etag(group)
        self.save(using=self._db)

    def apply_new_logo(self, logo):
        from . import aws_s3
        file_link = aws_s3.files_api._save_file_to_aws(bucket_name=settings.AWS_IMAGE_BUCKET_NAME, file=logo)
        self.avatar = file_link
        self.save(using=self._db)

    def delete(self, using=None, *args, **kwargs):
        try:
            import django.middleware.csrf, requests
            response = requests.delete('http://localhost:8090/delete/group/', params={'group_id': self.id})
            response.raise_for_status()
            return super().delete(using=using, *args, **kwargs)

        except() as exception:
            logger.debug('could not create user xmpp profile: [%s]' % exception)
            raise exceptions.XMPPGroupDeleteFailed()

class SongManager(models.Manager):

    def create(self, **kwargs):
        model = self.model(**kwargs)
        return model


class Song(object):

    objects = SongManager()

    subscription: typing.Optional[int]

    song_name: str
    song_description: typing.Optional[str]
    audio_file: bytes
    owner_id: int

    def delete(self, using=None, **kwargs):
        pass

class Admin(object):
    namespace = 'admin'


class Participant(object):
    namespace = 'participant'


class OutCast(object):
    namespace = 'outcast'


class Member(models.Model):

    objects = models.Manager()
    role: typing.Literal["admin", "outcast", "participant"]

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    group = models.OneToOneField(ChatGroup, on_delete=models.CASCADE)
    is_outcast = models.BooleanField(default=False)

    def get_members_profile(self):
        return self.user

    def change_role(self, role: typing.Literal["admin", "outcast", "participant"]):
        self.role = role
        self.save()