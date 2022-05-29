import typing

import asgiref.sync
import django.http
from django.template.response import TemplateResponse
from django.views.decorators.cache import cache_page

from rest_framework import views, permissions, status, decorators
from . import models, authentication, permissions as api_perms, forms

from .aws_s3 import files_api
import datetime, logging, rest_framework

from django.views.decorators import http, csrf, vary, cache
from django.db import transaction
import django.utils.decorators

logger = logging.getLogger(__name__)


class GetGroupAPIView(views.APIView):

    permission_classes = (

        permissions.AllowAny,
        api_perms.IsNotOutcast,
        permissions.IsAuthenticated,

    )
    authentication_classes = (authentication.UserAuthenticationClass,)

    @django.utils.decorators.method_decorator(decorator=cache.never_cache)
    def get(self, request):
        return django.template.response.TemplateResponse(context={'group': models.ChatGroup.objects.filter(
        group_name=request.query_params.get('group_name')).first(),
        'form': forms.SendGroupMessageForm()}, status=status.HTTP_200_OK,
        request=request, template='main/group_chat.html')


from django import urls
class CreateGroupAPIView(views.APIView):

    # permission_classes = (permissions.IsAuthenticated, )
    # authentication_classes = (authentication.UserAuthenticationClass, )

    @cache_page(60 * 5)
    def get(self, request):
        form = forms.CreateGroupForm()
        form.fields['members'].queryset = models.CustomUser.objects.all(
        ).exclude(username=request.user.username)  # user related friends...
        return TemplateResponse(request, 'main/create_group.html',
        context={'form': form}).render()

    @transaction.atomic
    def post(self, request):

        members = request.POST.get('members')
        group = models.ChatGroup.objects.create(**request.data,
        owner_jid=request.user.jid).members.update(members_func(members))

        if 'logo' in request.FILES.keys():
            group.apply_new_logo(logo=request.FILES.get('logo'))

        group.apply_new_etag()
        return django.http.HttpResponseRedirect(urls.reverse('main:get_group', kwargs={'group_name':
        group.group_name}))


class EditGroupAPIView(views.APIView):


    permission_classes = (permissions.IsAuthenticated, api_perms.IsGroupAdmin)
    authentication_classes = (authentication.UserAuthenticationClass,)


    @staticmethod
    def get_group_etag(request):
        group = models.ChatGroup.objects.get(group_name=request.query_params.get('group_name'))
        if not hasattr(group, 'etag'):
            group.etag = generate_etag(group=group)
            group.save()
        return group.etag


    @cache_page(60 * 2)
    def get(self, request):
        group = models.ChatGroup.objects.get(id=request.query_params.get('group_id'))
        form = forms.EditGroupForm(initial={elem: value for elem, value in group.__dict__.items()})
        response = TemplateResponse(request, context={'form': form}, template='main/edit_group.html')
        return response.render()


    @http.etag(etag_func=get_group_etag)
    @transaction.atomic
    @csrf.csrf_exempt
    def put(self, request):

        group = models.ChatGroup.objects.filter(group_name=request.query_params.get('group_name'))
        changed_fields = forms.EditGroupForm(request.POST, request.FILES).changed_data

        if 'logo' in changed_fields and len(request.FILES.keys()):

            group.apply_new_logo(logo=request.FILES.get('logo'))
            logger.debug('video file has been saved to amazon store...')
            changed_fields.remove('logo')

        for elem, value in request.data.items():
            if elem in changed_fields:
                setattr(group, elem, value)

        group.apply_new_etag()
        return django.http.HttpResponse(status=status.HTTP_200_OK)


from django.middleware.csrf import get_token
class DeleteGroupAPIView(views.APIView):

    # permission_classes = (api_perms.IsGroupOwner, permissions.IsAuthenticated,)
    # authentication_classes = (authentication.UserAuthenticationClass,)

    @csrf.requires_csrf_token
    def delete(self, request):
        try:
            models.ChatGroup.objects.get(id=request.query_params.get('group_id')).delete()
            return django.http.HttpResponseRedirect(reverse('main:main_page'))

        except django.core.exceptions.ObjectDoesNotExist:
            logger.debug('no such group found..')
            return django.http.HttpResponseNotFound()

        except django.db.IntegrityError as ine_err:
            logger.error('%s' % ine_err.args)
            return django.http.HttpResponseServerError()



class BanUserAPIView(views.APIView):


    permission_classes = (permissions.IsAuthenticated, api_perms.IsGroupAdmin,)
    authentication_classes = (authentication.UserAuthenticationClass,)


    def send_ban_request(self, request,  method, params):
        import requests

        api_url = 'http://localhost:8090/ban/or/unlock/user/'
        session = requests.Session()

        response = session.request(method=method, url=api_url,
        headers={'Access-Control-Allow-Origin': "*", 'CSRF-Token': django.middleware.csrf.get_token(request)},
        params={'username': params.get('username')})
        return response.status_code


    @staticmethod
    def change_role(request, role: str):
        try:
            group, user = models.CustomUser.objects.get(username='username'),\
            models.ChatGroup.objects.get(id=request.query_params.get('group_id'))
            models.Member.objects.get(user=user, group=group).change_role(role)

        except(django.core.exceptions.ObjectDoesNotExist,):
            return django.http.HttpResponseNotFound()


    @csrf.csrf_exempt
    def post(self, request):
        try:
            self.change_role(request, role='outcast')
            response_status_code = self.send_ban_request(
            request, request.method, params=request.query_params)
            return django.http.HttpResponse(status=response_status_code)
        except():
            return django.http.HttpResponseServerError(
            content=json.dumps({'error': 'Not Valid Username, user does not exist.'}),
            content_type='application/json')

    @csrf.csrf_exempt
    def delete(self, request):
        try:
            self.change_role(request, role='participant')
            response_status_code = self.send_ban_request(request,
            request.method, params=request.query_params)
            return django.http.HttpResponse(status=response_status_code)
        except():
            return django.http.HttpResponseServerError(
            content=json.dumps({'error': 'Invalid Username, user does not exist.'}),
            content_type='application/json')


from rest_framework import viewsets
class MembersViewSet(viewsets.ModelViewSet):

    def get_permissions(self):
        return (permissions.IsAuthenticated, api_perms.IsNotOutcast) if self.request.method in ('GET', 'HEAD') else\
        (api_perms.IsGroupAdmin, api_perms.IsNotOutcast, permissions.IsAuthenticated,)

    def get_authenticators(self):
        return (authentication.UserAuthenticationClass,)

    @decorators.action(methods=['get'], detail=False)
    def list(self, request):
        from django.db.models import Q
        group = models.ChatGroup.objects.get(id=request.query_params.get('group_id'))
        members = models.Member.objects.filter(Q(is_outcast=False) | Q(group=group))
        return django.http.JsonResponse({'members': members})


    @decorators.action(methods=['get'], detail=True)
    def retrieve(self, request):
        try:
            member = models.Member.objects.filter(user=models.CustomUser.objects.get(
            id=request.query_params.get('user_id'), group=models.ChatGroup.objects.get(id=
            request.query_params.get('group_id'))))
            return django.http.JsonResponse({'member': member})

        except(django.core.exceptions.ObjectDoesNotExist,):
            return django.http.HttpResponseServerError()


    @decorators.action(methods=['delete'], detail=False)
    @transaction.atomic()
    def destroy(self, request):
        try:
            user = models.CustomUser.objects.get(id=request.query_params.get('user_id'))
            models.Member.objects.delete(user=user)
            return django.http.HttpResponse(status=200)

        except(django.db.IntegrityError, django.core.exceptions.ObjectDoesNotExist,):
            return django.http.HttpResponseServerError()


    @decorators.action(methods=['post'], detail=False)
    @transaction.atomic
    def create(self, request):
        try:
            user = models.CustomUser.objects.get(id=request.query_params.get('user_id'))
            group = models.ChatGroup.objects.get(id=request.query_params.get('group_id'))

            member = models.Member.objects.create(user=user, group=group)
            member.role = 'participant'
            return django.http.HttpResponse(status=200)

        except(django.core.exceptions.ObjectDoesNotExist,):
            return django.http.HttpResponseServerError()


