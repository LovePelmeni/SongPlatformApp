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

    def has_permission(self, request, view):
        try:
            song = models.Song.objects.get(id=request.query_params.get('song_id'))
            if getattr(song, 'subscription'):
                if song.subscription in request.user.subscriptions.all():
                    return True
                return django.core.exceptions.PermissionDenied()
            return True
        except(django.core.exceptions.ObjectDoesNotExist, KeyError, AttributeError):
            return False


class HasSongPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        try:
            return models.Song.objects.get(
            id=request.query_params.get('song_id')).has_permission(request.user)
        except(django.core.exceptions.ObjectDoesNotExist,):
            return False

class IsAlbumOwner(permissions.BasePermission):

    def has_permission(self, request, view):
        try:
            return request.user in models.Album.objects.get(id=
            request.query_params.get('album_id')).owner.all()
        except(django.core.exceptions.ObjectDoesNotExist, AttributeError,):
            raise django.core.exceptions.PermissionDenied()




