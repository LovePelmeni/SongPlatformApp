from django.utils import deprecation
import django.http

from django.urls import reverse
from celery import shared_task
import jwt, logging, requests 

logger = logging.getLogger(__name__)


class SetUpAuthorizationHeaderMiddleware(deprecation.MiddlewareMixin):

    def process_request(self, request):
        try:
            request.META['Authorization'] = \
            'Bearer %s' % request.get_signed_cookie('jwt-token')
            return None
        except(KeyError,):
            return None


class CheckBlockedUserMiddleware(deprecation.MiddlewareMixin):

    def get_blocked_list(self):
        return models.BlockList.outcasts.all()

    def process_request(self, request):

        response = self.get_response(request)
        if not request.META.get('HTTP_REFERER'):
            return response

        if request.user in get_blocked_list():
            return django.http.HttpResponseForbidden()

        return response



class CsrfTokenCheckerMiddleware(deprecation.MiddlewareMixin):

    def process_request(self, request):
        try:
            if not 'CSRF-Token' in request.META.keys() and 'CSRF-Token' in request.COOKIES:
                request.META['CSRF-Token'] = request.COOKIES.get('CSRF-Token')
                return None
        except(KeyError,):
            return None

