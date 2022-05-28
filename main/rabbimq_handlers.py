import django.core.exceptions
import pika

import pydantic
from . import rabbitmq
from django.db import transaction
from django.conf import settings


def mark_event_as_delivered(method):
    rabbitmq.channel.basic_ack(delivery_tag=method.delivery_tag)
    # marking message with this delivery tag as delivered


import typing
class UserAPICredentials(pydantic.BaseModel):

    username: str
    balance: typing.Optional[int]

@transaction.atomic
def handle_user_creation(channel, method, properties, data):
    try:
        mark_event_as_delivered(method)
        user_credentials = UserAPICredentials(**json.loads(data.decode('utf-8'))
        if isinstance(data, bytes) else json.loads(data))

        models.APICustomer.objects.create(**user_credentials.dict())
        logger.debug('new api customer has been created...')

    except(django.db.IntegrityError,) as int_err:
        logger.error('[API EXCEPTION] %s .could not create user.' % int_err)

    except(pydantic.ValidationError,):
        logger.error('Invalid user credentials has been passed.')

@transaction.atomic
def handle_user_deletion(channel, method, properties, data):
    try:
        mark_event_as_delivered(method)
        json.loads(data.decode('utf-8'))
        models.APICustomer.objects.get(id=data['user_id']).delete()

    except(django.core.exceptions.ObjectDoesNotExist, django.db.IntegrityError,):
        logger.error('[API EXCEPTION]. Could not Delete API Customer')




