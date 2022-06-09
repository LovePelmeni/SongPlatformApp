import django.dispatch.dispatcher
from . import models

@django.dispatch.dispatcher.receiver(signal=models.CustomerCreated)
def create_customer(customer_data, **kwargs):
    pass

@django.dispatch.dispatcher.receiver(signal=models.CustomerUpdated)
def update_customer(updated_data, customer, **kwargs):
    pass

@django.dispatch.dispatcher.receiver(signal=models.CustomerDeleted)
def delete_customer(customer_id, **kwargs):
    pass

@django.dispatch.dispatcher.receiver(signal=models.SubscriptionCreated)
def create_subscription(subscription_data, **kwargs):
    pass

@django.dispatch.dispatcher.receiver(signal=models.SubscriptionUpdated)
def update_subscription(updated_data, subscription, **kwargs):
    pass

@django.dispatch.dispatcher.receiver(signal=models.SubscriptionDeleted)
def delete_subscription(subscription_id, **kwargs):
    pass



