import django.dispatch.dispatcher
from . import models

@django.dispatch.dispatcher.receiver(signal=models.CustomerCreated)
def create_customer(customer_data):
    pass

@django.dispatch.dispatcher.receiver(signal=models.CustomerUpdated)
def update_customer(updated_data, customer):
    pass

@django.dispatch.dispatcher.receiver(signal=models.CustomerDeleted)
def delete_customer(customer_id):
    pass



@django.dispatch.dispatcher.receiver(signal=models.SubscriptionCreated)
def create_subscription(subscription_data):
    pass

@django.dispatch.dispatcher.receiver(signal=models.SubscriptionUpdated)
def update_subscription(updated_data, subscription):
    pass

@django.dispatch.dispatcher.receiver(signal=models.SubscriptionDeleted)
def delete_subscription(subscription_id):
    pass


