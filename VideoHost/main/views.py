import django.http
import rest_framework.reverse
from django.shortcuts import render
from django.template.response import TemplateResponse

from django.views.decorators.cache import never_cache
from .aws_s3 import files_api

from django.conf import settings
from rest_framework.decorators import action

from rest_framework import status, permissions, views, decorators 
import logging, botocore.exceptions

from rest_framework.viewsets import ViewSet
from . import serializers, exceptions, models, permissions as api_perms, authentication

import os, django.core.exceptions
from django.views.decorators import vary
from django.utils.decorators import method_decorator

logger = logging.getLogger(__name__)

class MainAPIView(views.APIView):
    """Basically represents the main page of the application..."""

    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (authentication.UserAuthenticationClass, )

    @method_decorator(decorator=never_cache)
    def get(self, request):
        groups = request.user.chat_groups.all()
        return TemplateResponse(request, 'main/index.html',
        context={'title': 'Main Page',
        'groups': groups
        }).render()

@decorators.api_view(['GET'])
def get_blocked_page(request):
    return TemplateResponse(request, 'main/blocked_page.html', context=
    {'message': 'You are has been blocked at this group.'}).render()

@decorators.api_view(['GET'])
def healthcheck(request):
    return django.http.HttpResponse(status=200)




