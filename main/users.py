import django.http, django.core.exceptions
from rest_framework import views, status, permissions, decorators
from django.db import transaction
import datetime, json

from django.conf import settings
from django import db
from django import urls

from . import permissions as api_perms, models, dropbox as dropbox_storage,\
authentication, serializers as api_serializers

from .dropbox import files_api

import jwt, logging
from django.views.decorators import csrf, cache


logger = logging.getLogger(__name__)
success_codes = (code for code in range(200, 400))


def apply_jwt_token(user):
    try:
        token = jwt.encode(payload={'created_at': str(user.created_at), 'user_id': user.id},
        key=settings.SECRET_KEY, algorithm='HS256')
        return token 
    except jwt.PyJWTError:
        raise jwt.PyJWTError()


from django.contrib.auth.views import auth_logout


@transaction.atomic
@csrf.csrf_exempt
def delete_user(request):
    try:
        import jwt
        user_id = jwt.decode(request.META.get('Authorization').split(' ')[1],
        key=getattr(settings, 'SECRET_KEY'), algorithms='HS256').get('user_id')
        assert user_id

        response = django.http.HttpResponse(status=200)
        response.delete_cookie('jwt-token')

        auth_logout(request=request)
        models.CustomUser.objects.get(id=user_id).delete()
        return response

    except(db.IntegrityError, django.core.exceptions.ObjectDoesNotExist):
        return django.http.HttpResponseServerError()

    except(NotImplementedError, AttributeError):
        logger.debug('[USER-API-EXCEPTION]. Could not delete user profile. time - [%s]' % datetime.datetime.now())
        return django.http.HttpResponseServerError(content=json.dumps({'error': 'Delete Profile Failure'}))

    except() as exception:
        transaction.rollback()
        raise exception

class CreateUserAPIView(views.APIView):


    serializer_class = api_serializers.UserSerializer
    dropbox_storage = files_api.DropBoxBucket(
    getattr(settings, 'DROPBOX_CUSTOMER_AVATAR_FILE_PATH'))

    def check_permissions(self, request):
        if not request.META.get('Authorization'):
            return True
        return django.core.exceptions.PermissionDenied()


    def handle_exception(self, exc):
        if isinstance(exc, django.core.exceptions.ObjectDoesNotExist):
            return django.http.HttpResponseNotFound()
        return django.http.HttpResponse(status=status.HTTP_200_OK)


    @transaction.atomic
    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data, many=False)
            if serializer.is_valid(raise_exception=True):

                user = models.CustomUser.objects.create_user(**serializer.validated_data)

                if request.FILES.get('avatar_image'):
                    file = request.FILES.get('avatar_image')
                    file_link = self.dropbox_storage.upload(file=file, filename=file.name.split('.')[0])
                    user.avatar_link = file_link
                    user.save()
                try:
                    token = apply_jwt_token(user=user)
                    login(request, user, backend=getattr(settings, 'AUTHENTICATION_BACKENDS')[0])
                    response = django.http.HttpResponse(status=200)
                    response.set_signed_cookie('jwt-token', token)
                    return response

                except(db.IntegrityError, jwt.PyJWTError, NotImplementedError) as err:
                    logger.error('creation user failed! Error has occurred: %s' % err.args)
                    return django.http.HttpResponseServerError()

            return django.http.HttpResponse(status=status.HTTP_400_BAD_REQUEST)
        except(django.db.utils.IntegrityError, django.core.exceptions.BadRequest,) as exception:
            transaction.rollback()
            raise exception



class EditUserAPIView(views.APIView):

    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (authentication.UserAuthenticationClass, )

    def handle_exception(self, exc):
        if isinstance(exc, django.db.IntegrityError) or isinstance(exc, django.db.ProgrammingError):
            return django.http.HttpResponseServerError()
        return django.http.HttpResponseServerError()

    @csrf.requires_csrf_token
    @transaction.atomic
    def put(self, request):
        try:
            serializer = api_serializers.UserSerializer(request.data, many=False)
            if serializer.is_valid(raise_exception=True):

                if serializer.validated_data.get('avatar'):
                    request.user.apply_new_avatar(avatar=serializer.validated_data['avatar'])

                if 'password' in form.changed_data:
                    request.user.set_password(form.cleaned_data['password'])

                for elem, value in request.data.items():
                    request.user.__setattr__(elem, value)

                request.user.save()
            return django.http.HttpResponse(status=200)

        except(django.db.IntegrityError, django.db.ProgrammingError,) as exception :
            transaction.rollback()
            raise exception


import django.template.response
from django.conf import settings

from django.utils import decorators
from django.core.serializers.json import DjangoJSONEncoder


class CustomerProfileAPIView(views.APIView):

    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (authentication.UserAuthenticationClass,)

    def check_permissions(self, request):
        return self.get_authenticators()[0].authenticate(request)

    @decorators.method_decorator(cache.never_cache)
    def get(self, request):
        try:
            user_id = jwt.decode(request.get_signed_cookie('jwt-token'),
            key=getattr(settings, 'SECRET_KEY'), algorithms='HS256').get('user_id')

            user = list(models.CustomUser.objects.filter(id=user_id).values())
            return django.http.HttpResponse(content=json.dumps({'user': user},
            cls=DjangoJSONEncoder), status=status.HTTP_200_OK)

        except(KeyError, ):
            return django.http.HttpResponse(
            status=status.HTTP_404_NOT_FOUND)


from django.contrib.auth import\
authenticate, login


class LoginAPIView(views.APIView):

    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (authentication.UserAuthenticationClass,)

    @csrf.csrf_exempt
    def post(self, request):

        response = django.http.HttpResponse(status=200)
        user = authenticate(username=request.data.get('username'),

        password=request.data.get('password'))
        if user is not None:
            response.set_signed_cookie('jwt-token', apply_jwt_token(user))
            login(request, user, backend=getattr(settings, 'AUTHENTICATION_BACKENDS')[0])
            return response
        return django.http.HttpResponse(status=400)



