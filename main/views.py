import django.http
from django.template.response import TemplateResponse

from django.views.decorators.cache import never_cache

from rest_framework import permissions, views, decorators
import logging

from . import authentication

import django.core.exceptions
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




