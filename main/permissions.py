from rest_framework import permissions
import django.core.exceptions
from . import models


class IsNotSubscriptionOwner(permissions.BasePermission):

    def has_permission(self, request, view):
        try:
            api_user = models.APICustomer.objects.get(id=request.query_params.get('customer_id'))
            if not request.query_params.get('sub_id') in models.Subscription.objects.filter(owner_id=api_user.id):
                return True
            raise django.core.exceptions.PermissionDenied()

        except(django.core.exceptions.ObjectDoesNotExist):
            raise django.core.exceptions.PermissionDenied()

class HasAlreadySubscription(permissions.BasePermission):

    def has_permission(self, request, view):
        user = models.APICustomer.objects.filter(id=request.query_params.get('customer_id')).first()
        sub_id = request.query_params.get('sub_id')
        if not sub_id in user.purchased_subs.values_list('id', flat=True):
            return True
        raise django.core.exceptions.PermissionDenied()


