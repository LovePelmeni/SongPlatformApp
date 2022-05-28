from django.contrib import admin
from . import models

# Register your models here.
@admin.register(models.APICustomer)
class APICustomerAdmin(admin.ModelAdmin):

    list_display = ['username', 'balance']
    fields = ('username', 'balance')

@admin.register(models.Subscription)
class SubscriptionAdmin(admin.ModelAdmin):

    list_display = ('subscription_name', 'amount', 'owner_id')
    fields = ('subscription_name', 'amount', 'owner_id')




