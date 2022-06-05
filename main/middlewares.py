from django.utils import deprecation
import django.http

from django.urls import reverse
from celery import shared_task
import jwt, logging, requests 

logger = logging.getLogger(__name__)


class CheckUserAuthMiddleware(deprecation.MiddlewareMixin):

    def process_request(self, request):
        if not request.get_signed_cookie('jwt-token'):
            return django.http.HttpResponseRedirect(reverse('main:registry'))
        return None

class CheckBlockedUserMiddleware(deprecation.MiddlewareMixin):

    def process_request(self, request):
        try:
            if request.user.is_blocked:
                return django.http.HttpResponseRedirect(reverse('main:blocked_page'))
            return None
        except AttributeError:
            return None

class StatisticMiddleware(deprecation.MiddlewareMixin):

    async def update_statistic(self, views: int):
        pass

    def process_request(self, request):
        pass
