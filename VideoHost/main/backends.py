from django.contrib.auth import backends, login
import django.core.exceptions
from . import models

class AdminAuthBackend(backends.RemoteUserBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = models.CustomUser.objects.filter(username__iexact=username).first()
            if user.check_password(password) and user.is_staff:
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                return user
            return None
        except django.core.exceptions.ObjectDoesNotExist:
            return None

    def get_all_permissions(self, user_obj, obj=None):
        if user_obj.is_anonymous:
            return django.core.exceptions.PermissionDenied()
        return True

class UserAuthBackend(backends.RemoteUserBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = models.CustomUser.objects.filter(username__iexact=username).first()
            if user.check_password(password) and not user.is_staff:
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                return user
            return None
        except django.core.exceptions.ObjectDoesNotExist:
            return None

    def get_all_permissions(self, user_obj, obj=None):
        if user.is_anonymous:
            return django.core.exceptions.PermissionDenied()
        return True


