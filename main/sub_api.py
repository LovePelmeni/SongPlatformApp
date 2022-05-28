from __future__ import annotations
from . import mongo_api, sub_tasks, models, signals

from django_celery_beat import models as celery_models
from celery import shared_task

import typing, django.db, logging, json, django.utils.timezone,\
dataclasses, pydantic, celery.exceptions, datetime


logger = logging.getLogger(__name__)


class SubscriptionDocument(pydantic.BaseModel):
    """Represents the Model of the subscription document"""

    owner_id: int
    purchaser_id: int

    subscription_id: int
    subscription_name: typing.Optional[str]

    amount: int
    currency: typing.Literal["usd", "rub", "eu"]
    active: bool

    subscription_task_id: typing.Optional[int] # Task id that represents model object of PeriodTask
    created_at: typing.Optional[str]
    idempotency_key: typing.Optional[str]


    def __init__(self, **kwargs):

        kwargs.update({'idempotency_key': self.generate_idempotency_key(kwargs),
        'created_at': kwargs['created_at'].strftime('%H:%d:%m')})
        self.update_forward_refs(**kwargs)
        super(SubscriptionDocument, self).__init__(**kwargs)


    @staticmethod
    def generate_idempotency_key(kwargs) -> str:
        return '%s-%s-%s-%s-%s' % (kwargs.get('owner_id'), kwargs.get('purchaser'),
        kwargs.get('amount'), kwargs.get('currency'),
        kwargs.get('created_at').strftime('%H:%d:%m'))


def unapply_subscription(idempotency_key):
    try:
        document = mongo_api.get_subscription_document(key=idempotency_key)
        sub_tasks.delete_subscription_task(document.get('subscription_task_id'))
        signals.remove_purchaser.send(sender=unapply_subscription,
        purchaser_id=document.get('purchaser_id'), subscription_id=document.get('subscription_id'))
        logger.debug('subscription has been canceled.')


    except(django.db.IntegrityError, NotImplementedError) as exception:
        logger.error('Exception while canceling subscription. %s' % exception)
        raise django.db.IntegrityError

    except(django.core.exceptions.ObjectDoesNotExist, AttributeError) as exception:
        logger.error('%s Exception has occurred, while was canceling subscription.' % exception.__class__.__name__)
        raise django.core.exceptions.ObjectDoesNotExist



def apply_subscription(purchaser_id, subscription_id, document, idempotency_key):
    try:
        task_id = sub_tasks.create_subscription_task(document=document,
        subscription_id=subscription_id, purchaser_id=purchaser_id, idempotency_key=idempotency_key).id

        signals.add_purchaser.send(sender=apply_subscription, purchaser_id=document.purchaser_id,
        subscription_id=document.subscription_id)
        logger.debug('subscription applied.')
        return task_id

    except(django.db.IntegrityError, django.core.exceptions.ObjectDoesNotExist,) as exception:
        logger.error('could not create subscription task. Exception: %s' % exception)
        raise exception

