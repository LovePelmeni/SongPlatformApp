from __future__ import annotations

import typing

import pika
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin

from django.db import models

# from .distributed_transactions import distributed_transaction_checker
import django.dispatch

from django import db
from django.core import validators, exceptions
from django.db import transaction

EVENTS = ["customer_create", "customer_delete", "customer_update", "sub_create", "sub_delete", "sub_update"]
import json

class DistributedController(object):
    """
    / * Class Represents the distributed transaction controller
        that allows making changes across all services in the whole project.
        Basically is used for create/edit/delete/ customers and subscriptions data
        in order to make the other services up-to-date of the information about events, happen on the main line

        It Uses RabbitMQ as a message (event) delivery, that allows to make quick changes.
    """
    def __init__(self, event_name:
    typing.Literal["customer_create", "customer_delete",
    "customer_update", "sub_create", "sub_delete", "sub_update"],
    request_body: dict | str,
    client_credentials=None
    ):
        self.event_name = event_name
        self.client_connection_credentials = client_credentials if client_credentials else None
        self.request_body = json.dumps(request_body) if not isinstance(request_body, str) else request_body
        self.exchange = 'exchange'

    @staticmethod
    def rabbitmq_connection() -> typing.Generator[pika.BlockingConnection.channel]:
        import pika.exceptions
        try:
            yield pika.BlockingConnection(parameters=pika.ConnectionParameters(
            credentials=(settings.RABBITMQ_USER, settings.RABBITMQ_PASSWORD),
            host=settings.RABBITMQ_HOST, port=settings.RABBITMQ_PORT, virtual_host=settings.RABBITMQ_VHOST)).channel()

        except(pika.exceptions.ChannelError, pika.exceptions.AMQPError, pika.exceptions.ConnectionClosed) as exception:
            logger.error('[EXCEPTION OCCURRED WHILE CONNECTING RABBITMQ CLIENT TO THE SERVER]: %s' % exception)
            raise NotImplementedError

    def __call__(self, *args, **kwargs):
        import pika
        try:
            with rabbitmq_connection() as connection_channel:
                connection_channel.basic_publish(routing_key=self.event_name,
                body=self.request_body, exchange=self.exchange)
            return True
        except(NotImplementedError,):
            raise


distributed_controller = DistributedController

class PhoneNumberField(models.CharField):

    def __init__(self, **kwargs):
        self.max_length = kwargs.get('max_length')
        super(PhoneNumberField, self).__init__(**kwargs)

    def validate(self, value, instance):
        for regex in self.phone_number_regexes:
            if re.match(pattern=regex, string=value):
                return value
        raise django.core.exceptions.ValidationError(message='Invalid Phone Number')

    def db_type(self, connection):
        return 'char(%s)' % 100

    def to_python(self, value):
        return value


class CustomManager(BaseUserManager):

    def create_user(self, **kwargs):
        try:
            user = self.model(**kwargs)
            user.set_password(raw_password=kwargs.get('password'))
            user.save(using=self._db)
            return user
        except(distributed_transaction_checker.DistributedTransactionFailed,):
            raise NotImplementedError()

    def create_superuser(self, username, password, phone_number):
        user = self.model(username=username, password=password, phone_number=phone_number, is_staff=True)
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):

    objects = CustomManager()

    username = models.CharField(verbose_name='Username', max_length=100, unique=True)
    phone_number = PhoneNumberField(verbose_name='Phone Number', max_length=100, null=False)

    avatar_image = models.CharField(verbose_name='AWS User Avatar Link', null=True, max_length=100)

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


    def delete(self, using=None, **kwargs):
        try:
           self.distributed_delete()
           return super().delete(using=using, **kwargs)
        except() as exception:
            raise exception


    def create(self, **kwargs):
        return self.distributed_create(**kwargs)


    def update(self, **kwargs):
        return self.distributed_update(**{'customer_name': self.username,
        'customer_id': self.id, 'updated_data': kwargs})


    def distributed_create(self, **kwargs) -> DistributedController:
        # result = distributed_controller(event_name='customer_create',
        # client_credentials=None, request_body=kwargs)
        # return result
        pass

    def distributed_update(self, **kwargs) -> DistributedController:
        # result = distributed_controller(event_name='customer_update',
        # client_credentials=None, request_body=kwargs)
        # return result
        pass

    def distributed_delete(self, **kwargs) -> DistributedController:
        # result = distributed_controller(event_name='customer_delete',
        # client_credentials=None, request_body=kwargs)
        # return result
        pass


class Song(models.Model):

    objects = models.Manager()

    has_subscription = models.BooleanField(verbose_name='Has Subscription song.', null=False, default=False)
    owners = models.ManyToManyField(CustomUser, related_name='songs', null=True)
    preview = models.CharField(verbose_name='AWS Preview File link', max_length=100, null=True)

    song_name = models.CharField(verbose_name='Song Name', null=False, max_length=100)
    song_description = models.TextField(verbose_name='Song Description', null=True, max_length=100)
    audio_file = models.CharField(verbose_name='AWS Audio File Link', null=False, max_length=300)

    def delete(self, using=None, **kwargs):
        from . import aws_s3
        aws_s3.files_api._delete_from_aws_storage(file_link=kwargs.get('file_link'))
        return super().delete(using=using, **kwargs)

    @staticmethod
    def get_etag(song):
        return "%s-%s" % (song.song_name, datetime.datetime.now())

    def set_etag(self, etag):
        self.etag = etag
        self.save()

    def has_permission(self, user):
        import django.core.exceptions
        if user in self.owners.all():
            return True
        raise django.core.exceptions.PermissionDenied()

class SubscriptionQueryset(models.QuerySet):
    """
    / * Queryset that represents subscription Model object
    """
    @transaction.atomic
    def create(self, **kwargs):
        try:
            model = self.model(**kwargs)
            model.distributed_create()
            return model
        except(NotImplementedError,):
            raise NotImplementedError

    @transaction.atomic
    def update(self, **kwargs):
        pass

    @transaction.atomic
    def delete(self):
        pass

class SubscriptionManager(db.models.manager.BaseManager.from_queryset(queryset_class=SubscriptionQueryset)):
    pass

currency = [
    ('RUB', 'rub'),
    ('USD', 'usd'),
    ('EUR', 'eur')
]

class Subscription(models.Model):

    objects = SubscriptionManager()
    non_updated_fields = ('owner', 'amount', 'currency')

    owner = models.OneToOneField(to=CustomUser, on_delete=models.CASCADE)
    subscription_name = models.CharField(verbose_name='Subscription Name', max_length=100)

    songs = models.ForeignKey(to=Song, null=True, on_delete=models.PROTECT, related_name='subscription')
    amount = models.IntegerField(verbose_name='Amount', null=False)
    currency = models.CharField(choices=currency, verbose_name='Currency', null=False, max_length=100)

    def __str__(self):
        return self.subscription_name

    def distributed_create(self, new_credentials: dict):

        import requests
        response = requests.post('http://transaction_app:8095:/create/customer/')
        response.raise_for_status()

    def distributed_delete(self, fields=None):
        import requests
        response = requests.delete('http://transaction_app:8095:/delete/customer/')
        response.raise_for_status()

    def distributed_update(self, updated_data: dict):
        import requests
        response = requests.put('http://transaction_app:8095:/edit/customer/')
        response.raise_for_status()
        pass

    def has_permission(self, user):
        return user in self.owners.all()

    def update_or_restrict(self, new_values: dict):
        restricted_list = []
        for elem, value in new_values.items():
            if elem not in self.non_updated_fields:
                self.__setattr__(elem, value)
            else:
                restricted_list.append(elem)
        return restricted_list

class Album(models.Model):

    album_name = models.CharField(verbose_name='Album Name', max_length=100, null=False)
    songs = models.ManyToManyField(verbose_name='Songs', null=True, to=Song)
    owner = models.OneToOneField(verbose_name='Owner', null=False, to=CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.album_name


class StatSong(models.Model):

    song = models.OneToOneField(verbose_name='Song to track.',
    on_delete=models.CASCADE, null=False, to=Song, related_name='statistic')
    views = models.IntegerField(verbose_name='Views')

    def __str__(self):
        return self.song.id






