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


class CheckBlockedUserMiddleware(object):

    def get_blocked_list(self):
        return models.BlockList.outcasts.all()

    def __init__(self, get_response):
        self.get_response = get_response
        super(CheckBlockedUserMiddleware, self).__init__(get_response)

    def __call__(self, request):

        response = self.get_response(request)
        if not request.META.get('HTTP_REFERER'):
            return response

        if request.user in get_blocked_list():
            return django.http.HttpResponseForbidden()

        return response



