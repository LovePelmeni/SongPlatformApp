from rest_framework import permissions
from . import models
import logging
import django.core.exceptions

logger = logging.getLogger(__name__)


class IsNotAuthorizedOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        try:
            if not request.get_signed_cookie('jwt-token'):
                return True
            if request.method in permissions.SAFE_METHODS:
                return True
            else:
                return False
        except(KeyError):
            return True

class IsNotBlocked(permissions.BasePermission):

    def has_permission(self, request, view):
        if not request.user.is_blocked:
            return True
        raise django.core.exceptions.PermissionDenied()


class HasSubscription(permissions.BasePermission):


    def has_sub_permission(self, user_id, sub_id):
        import requests
        response = requests.get('http://localhost:8076/has/sub/permission/',
        params={'customer_id': user_id, 'sub_id': sub_id}, timeout=10)
        return json.loads(response.text)['sub_property']


    def has_permission(self, request, view):
        song = models.Song.objects.get(id=request.query_params.get('song_id'))
        if getattr(song, 'subscriptions'):
            if self.has_sub_permission(user_id=request.user.id,
            sub_id=song.subscription.dict().get('subscription_id')):
                return True
            return django.core.exceptions.PermissionDenied()
        return True


