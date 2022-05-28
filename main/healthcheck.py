import health_check.exceptions
from rest_framework import decorators

import django.http, subprocess, django.utils.decorators
from health_check.backends import BaseHealthCheckBackend

from health_check.views import MainView
from rest_framework import status

from django.views.decorators import cache
import typing
from .celery_register import celery_module as celery_app


class CeleryHealthCheckAPIBackend(BaseHealthCheckBackend):

    critical_service = False

    def check_status(self):
        try:
            pass
            inspect = celery_app.celery_app.control.inspect()
            available = inspect.ping()
            if not available:
                raise health_check.exceptions.HealthCheckException
        except():
            raise health_check.exceptions.HealthCheckException(
                message='Celery Does not Responding.'
            )

    def identifier(self):
        return 'Celery Health Check'

import requests
class CeleryHealthCheckAPIView(MainView, CeleryHealthCheckAPIBackend):

    @django.utils.decorators.method_decorator(decorator=cache.never_cache)
    def get(self, request, **kwargs):
        try:
            return self.render_to_response_json(
            (CeleryHealthCheckAPIBackend, ))
        except(health_check.exceptions.HealthCheckException,):
            return django.http.HttpResponse(status=status.HTTP_503_SERVICE_UNAVAILABLE)

    def render_to_response_json(self, plugins: typing.Any, **kwargs) -> django.http.JsonResponse:
        return django.http.JsonResponse({
            'result': {p.identifier(): p.check_status()} for p in plugins
        })

@decorators.api_view(['GET'])
def application_service_healthcheck(request):
    return django.http.HttpResponse(status=200)



