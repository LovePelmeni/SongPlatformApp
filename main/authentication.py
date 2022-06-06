import typing

import asgiref.sync
import django.core.exceptions

import rest_framework.exceptions
from rest_framework import authentication
from rest_framework.authentication import get_authorization_header

import jwt, json
from django.conf import settings

import logging
from . import models

logger = logging.getLogger(__name__)


class UserAuthenticationClass(authentication.BaseAuthentication):

    authorization_header_prefix = 'bearer'

    def authenticate(self, request):

        if not 'Authorization' in request.headers.keys():
            raise rest_framework.exceptions.PermissionDenied()
        try:
            auth = get_authorization_header(request).split(' ')
            if not auth[1] or not auth[0].lower() in ('bearer', 'token'):
                raise rest_framework.exceptions.AuthenticationFailed()

            payload = jwt.decode(auth[1], algorithms='HS256', key=settings.SECRET_KEY)
            logger.debug('user jwt has been passed...')
            if models.CustomUser.objects.filter(username=json.loads(payload['username'])).first():
                return None
            raise rest_framework.exceptions.AuthenticationFailed()

        except jwt.PyJWTError:
            raise rest_framework.exceptions.AuthenticationFailed()
