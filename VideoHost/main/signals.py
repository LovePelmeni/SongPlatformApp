import django.dispatch.dispatcher
from . import models
import django.core.exceptions

@django.dispatch.dispatcher.receiver(signal=models.CustomerCreated)
def create_customer(customer_data, **kwargs):
    models.CustomUser.objects.create(**customer_data)

@django.dispatch.dispatcher.receiver(signal=models.CustomerUpdated)
def update_customer(updated_data, customer_id, **kwargs):
    try:
        customer = models.CustomUser.objects.get(id=customer_id)
        for element, value in updated_data.items():
            customer.__setattr__(element, value)
    except(django.core.exceptions.ObjectDoesNotExist,):
        pass

@django.dispatch.dispatcher.receiver(signal=models.CustomerDeleted)
def delete_customer(customer_id, **kwargs):
    try:
        models.CustomUser.objects.delete(id=customer_id)
    except(django.core.exceptions.ObjectDoesNotExist):
        pass

@django.dispatch.dispatcher.receiver(signal=models.SubscriptionCreated)
def create_subscription(subscription_data, **kwargs):
    models.Subscription.objects.create(**subscription_data)

@django.dispatch.dispatcher.receiver(signal=models.SubscriptionUpdated)
def update_subscription(updated_data, subscription_id, **kwargs):
    try:
        subscription = models.Subscription.objects.get(id=subscription_id)
        for element, value in updated_data.items():
            subscription.__setattr__(element, value)
    except(django.core.exceptions.ObjectDoesNotExist):
        pass

@django.dispatch.dispatcher.receiver(signal=models.SubscriptionDeleted)
def delete_subscription(subscription_id, **kwargs):
    try:
        models.Subscription.objects.delete(id=subscription_id)
    except(django.core.exceptions.ObjectDoesNotExist,):
        pass




