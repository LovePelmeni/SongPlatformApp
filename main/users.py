import django.http, django.core.exceptions
from rest_framework import views, status, permissions, decorators
from django.db import transaction

from django import db
from django import urls

from . import permissions as api_perms, models, forms, aws_s3, authentication, serializers as api_serializers
from .aws_s3 import exceptions
import jwt, logging
from django.views.decorators import csrf


logger = logging.getLogger(__name__)
success_codes = (code for code in range(200, 400))


def apply_jwt_token(user):
    try:
        token = jwt.encode(payload={'created_at': str(user.created_at), 'user_id': user.id},
        key=settings.SECRET_KEY, algorithm='HS256')
        return token 
    except jwt.PyJWTError:
        raise jwt.PyJWTError()


@decorators.api_view(['DELETE'])
def delete_user(request):
    try:
        request.user.delete()
        return django.http.HttpResponse(status=status.HTTP_200_OK)

    except(db.IntegrityError,):
        return django.http.HttpResponseServerError()

    except(exceptions.XMPPUserDeleteFailed,):
        logger.debug('[USER-API-EXCEPTION]. Could not delete user profile. time - [%s]' % datetime.datetime.now())
        return django.http.HttpResponseServerError(content=json.dumps({'error': 'Delete Profile Failure'}))


class CreateUserAPIView(views.APIView):


    permission_classes = (api_perms.IsNotAuthorizedOrReadOnly, permissions.AllowAny,)
    serializer_class = api_serializers.UserSerializer
    renderer_classes = (renderers.JSONRenderer,)


    @cache.cache_page(60 * 5)
    def get(self, request):
        return django.template.response.TemplateResponse(request,
        template='main/register.html', context={'form': forms.CreateUserForm()}).render()


    @transaction.atomic
    def post(self, request):

        serializer = self.serializer_class(data=request.data, many=False)
        if serializer.is_valid(raise_exception=True):

            user = models.CustomUser.objects.create_user(**serializer.validated_data)

            if request.FILES.get('avatar_image'):
                aws_s3.files_api._save_file_to_aws(request, user)
            try:
                token = apply_jwt_token(user=user)
                login(request, user, backend=getattr(settings, 'AUTHENTICATION_CLASSES')[0])
                response = django.http.HttpResponseRedirect(urls.reverse('main:main_page'))
                response.set_signed_cookie('jwt-token', token)
                return response

            except(db.IntegrityError, jwt.PyJWTError) as err:
                logger.error('creation user failed! Error has occurred: %s' % err.args)
                return django.http.HttpResponseServerError()

            except(exceptions.XMPPUserCreationFailed,):
                logger.debug('[USER-API-EXCEPTION], operation CREATE FAILED. time - [%s]' % (datetime.datetime.now()))

        return django.http.HttpResponse(status=status.HTTP_400_BAD_REQUEST)



class EditUserAPIView(views.APIView):

    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (authentication.UserAuthenticationClass, )


    @cache.cache_page(60 * 5)
    def get(self, request):
        return django.template.response.TemplateResponse(request, 'main/edit_profile.html',
        context={'form': forms.EditUserForm(initial={elem: value for elem, value in request.user.__dict__.items()})})


    @transaction.atomic
    def put(self, request):
        form = forms.EditUserForm(request.data)

        for elem, value in request.data.items():
            request.user.__setattr__(elem, value)

        if 'avatar_image' in form.changed_data:
            request.user.apply_new_avatar(avatar=form.cleaned_data['avatar'])

        if 'password' in form.changed_data:
            request.user.set_password(form.cleaned_data['password'])

        request.user.save()
        return django.http.HttpResponseRedirect(reverse('main:get_user_profile'))



import django.template.response
from django.conf import settings


@decorators.action(methods=['get', 'head'], detail=True)
@decorators.permission_classes([permissions.IsAuthenticated, ])
@decorators.authentication_classes([authentication.UserAuthenticationClass])
def get_user_profile(request):

    user_id = jwt.decode(request.get_signed_cookie('jwt-token'),
    key=getattr(settings, 'SECRET_KEY'), algorithms='HS256').get('user_id')

    user = models.CustomUser.objects.filter(id=user_id).first()
    return django.template.response.TemplateResponse(request, template='main/profile.html',
    context={'user': user}).render()


from django.contrib.auth import\
authenticate, login


class LoginAPIView(views.APIView):

    permission_classes = (permissions.AllowAny,)

    @cache.cache_page(timeout=60 * 5)
    def get(self, request):
        return django.template.response.TemplateResponse(
        request, 'main/index.html', {'form': forms.LoginForm()})

    @csrf.csrf_exempt
    def post(self, request):
        response = django.http.HttpResponseRedirect(reverse('main:main_page'))
        user = authenticate(username=request.data.get('username'),
        password=request.data.get('password'))
        if user is not None:
            request.set_signed_cookie(apply_jwt_token(user))
            login(request, user, backend=getattr(settings, 'AUTHENTICATION_CLASSES')[0])

            return response
        return django.http.HttpResponse(status=400)



