from django.utils import deprecation
import django.http

from django.urls import reverse
from celery import shared_task
import jwt, logging, requests 

logger = logging.getLogger(__name__)

class SetUpAuthorizationHeaderMiddleware(deprecation.MiddlewareMixin):

    def process_request(self, request):
        try:
            if not request.headers.get('Authorization'):
                request.headers['Authorization'] = request.get_signed_cookie('jwt-token')
            return None
        except(KeyError,):
            return None


class CheckBlockedUserMiddleware(deprecation.MiddlewareMixin):

    def process_request(self, request):
        try:
            if request.user.is_blocked:
                request.headers['IS_BLOCKED'] = True
                return None
        except AttributeError:
            return None





