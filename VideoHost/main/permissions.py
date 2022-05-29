from rest_framework import permissions
from . import models
import logging
import django.core.exceptions

logger = logging.getLogger(__name__)

class IsAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        group = models.ChatGroup.objects.filter(group_name=request.query_params['group_name']).first()
        if not request.user in group.admins.all():
            return django.core.exceptions.PermissionDenied()
        return True

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

class CheckIsBlockedOrNotMemberUser(permissions.BasePermission):

    def has_permission(self, request, view):

        group = models.ChatGroup.objects.get(group_name=request.query_params.get('group_name'))
        if not request.user in group.members.all() or request.user.is_blocked:
            logger.debug('permission not allowed...')
            raise django.core.exceptions.PermissionDenied()
        return True

class IsNotBlocked(permissions.BasePermission):

    def has_permission(self, request, view):
        if not request.user.is_blocked:
            return True
        raise django.core.exceptions.PermissionDenied()

class IsNotOutcast(permissions.BasePermission):

    def has_permission(self, request, view):
        try:
            group = models.ChatGroup.objects.get(id=request.query_params.get('group_id'))
            if models.Member.objects.get(user=request.user, group=group).is_outcast:
                return django.core.exceptions.PermissionDenied()
            return True
        except(django.core.exceptions.ObjectDoesNotExist, AssertionError):
            return False

class IsGroupAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        try:
            group = models.ChatGroup.objects.get(id=request.query_params.get('group_id'))
            if models.Member.objects.get(user=request.user, group=group).role == 'admin':
                return True
            return django.core.exceptions.PermissionDenied()
        except(AssertionError, django.core.exceptions.ObjectDoesNotExist):
            return False



