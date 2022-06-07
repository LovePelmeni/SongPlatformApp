import django.core.exceptions
from rest_framework import generics, viewsets, mixins, decorators, status, permissions

from . import models, authentication, permissions as api_permissions, dropbox as dropbox_storage
import django.http
from django.db import models as db_models

from django.conf import settings
from django.views.decorators import http, cache, csrf

from django.db import transaction
from . import serializers
import json, django.core.serializers.json


class SongCatalogViewSet(viewsets.ModelViewSet):

    queryset = models.Song.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    authentication_classes = (authentication.UserAuthenticationClass,)

    def get_request_user(self, request):
        import jwt
        user_id = jwt.decode(request.get_signed_cookie('jwt-token'),
        key=settings.SECRET_KEY, algorithms='HS256').get('user_id')
        return models.CustomUser.objects.get(id=user_id)


    def handle_exception(self, exc):
        if exc.__class__.__name__ in (django.core.exceptions.PermissionDenied, django.http.HttpResponseForbidden):
            return django.http.HttpResponse(status=status.HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS)

        if isinstance(exc, django.core.exceptions.ObjectDoesNotExist):
            return django.http.HttpResponseNotFound()

        return django.http.HttpResponseServerError()


    def check_object_permissions(self, request, song):
        if not song in request.user.songs.all() \
        or not song.subscrition in request.user.subscriptions.all():
            raise django.core.exceptions.PermissionDenied()


    @decorators.action(methods=['get'], detail=True, description='Obtain Single Song Object.')
    def retrieve(self, request, *args, **kwargs):
        try:
            song = models.Song.objects.get(id=request.query_params.get('song_id')).select_related('statistic')
            song.statistic.views += 1
            song.save()
            self.check_object_permissions(request=request, song=song)
            return django.http.HttpResponse(status=200, content=json.dumps({'song': song}))

        except(django.core.exceptions.ObjectDoesNotExist, KeyError, AttributeError):
            return django.http.HttpResponseNotFound()

        except(django.core.exceptions.PermissionDenied,):
            raise django.core.exceptions.PermissionDenied()


    @decorators.action(methods=['get'], detail=False, description='Obtain Song Queryset.')
    def list(self, request, *args, **kwargs):
        """
        / * Returns song query with following annotation:
        if song "subscription" in user subscriptions, then available, else Not
        """
        try:
            from django.db import models as db_models
            user = self.get_request_user(request)

            user_subs = user.subscriptions.all() if getattr(user, 'subscriptions') else []
            queryset = self.queryset.annotate(is_available=db_models.Value(
            db_models.F('subscription') in user_subs, output_field=db_models.BooleanField()))

            return django.http.HttpResponse(json.dumps({'queryset': list(queryset.values())},
            cls=django.core.serializers.json.DjangoJSONEncoder), status=200)

        except(django.core.exceptions.ObjectDoesNotExist, AttributeError) as exception:
            raise exception


import typing
from django.db import models as db_models

class TopWeekSongsViewSet(viewsets.ModelViewSet):

    permission_classes = (permissions.AllowAny,)
    queryset = models.Song.objects.all()
    authentication_classes = (authentication.UserAuthenticationClass,)

    def handle_exception(self, exc):
        if isinstance(exc, django.core.exceptions.ObjectDoesNotExist):
            return django.http.HttpResponseNotFound()
        return django.http.HttpResponseServerError()

    @decorators.action(methods=['get'], detail=True)
    def retrieve(self, request, *args, **kwargs):
        try:
            song_id = request.query_params.get('song_id')
            song = self.get_most_viewed_queryset(
            models.Song.objects.get(id=song_id))

            return django.http.HttpResponse(json.dumps({'song': song},
            cls=django.core.serializers.json.DjangoJSONEncoder))

        except(django.core.exceptions.ObjectDoesNotExist) as exception:
            raise exception

    def get_most_viewed_queryset(self, queryset) -> db_models.QuerySet:
        """
        / * returns most listened songs during this week.
        // * joins with Song queryset by song ID.
        """
        try:
            general_query = self.get_queryset().select_related('statistic').annotate(
            views_count=db_models.F('statistic__views')).order_by(db_models.F('views_count').desc())[:10]
            return general_query
        except(AttributeError,):
            raise NotImplementedError

    @decorators.action(methods=['get'], detail=False)
    def list(self, request, *args, **kwargs):
        parsed_queryset = list(self.get_most_viewed_queryset(self.get_queryset()).values())
        return django.http.HttpResponse(
        content=json.dumps({'queryset': parsed_queryset},
        cls=django.core.serializers.json.DjangoJSONEncoder), status=200)


class SongGenericView(generics.GenericAPIView):

    queryset = models.Song.objects.all()
    permissions = (api_permissions.HasSongPermission, permissions.IsAuthenticated,)
    authentication_classes = (authentication.UserAuthenticationClass,)
    song_bucket = dropbox_storage.files_api.DropBoxBucket(
    path=getattr(settings, 'DROPBOX_SONG_AUDIO_FILE_PATH'))

    def handle_exception(self, exc):

        if isinstance(exc, django.core.exceptions.ValidationError):
            return django.http.HttpResponseBadRequest()

        if isinstance(exc, django.core.exceptions.ObjectDoesNotExist):
            return django.http.HttpResponseNotFound()

        if isinstance(exc, django.core.exceptions.PermissionDenied):
            return django.http.HttpResponse(status=status.HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS)

        return django.http.HttpResponseServerError()

    @csrf.csrf_exempt
    def post(self, request):
        status_code = 400
        if serializers.SongCreateSerializer(data=request.data, many=False).is_valid(raise_exception=True):
            models.Song.objects.create(**request.data)
            status_code = 200
        return django.http.HttpResponse(status=status_code)

    @csrf.csrf_exempt
    @transaction.atomic
    def put(self, request):
        try:
            song = self.get_queryset().get(id=request.query_params.get('song_id'))
            serializer = serializers.SongUpdateSerializer(data=request.data, many=False)

            if serializer.is_valid(raise_exception=True):
                if 'preview' in request.FILES.keys():

                    filename = request.FILES.get('preview').name.split('.')[0]
                    file_link = self.song_bucket.upload(file=request.FILES.get('preview'),
                    filename='%s-%s' % (filename, datetime.datetime.now()))
                    serializer.validated_data.update({'preview': file_link.dict().get('file_link')})

                for elem, value in serializer.validated_data.items():
                    song.__setattr__(elem, value)

                song.save()
                return django.http.HttpResponse(status=200)

        except() as exception:
            transaction.rollback()
            raise exception

    @csrf.csrf_exempt
    @transaction.atomic
    def delete(self, request):
        try:
            self.get_queryset().get(
            id=request.query_params.get('song_id')).delete()
            return django.http.HttpResponse(status=status.HTTP_200_OK)

        except(django.core.exceptions.ObjectDoesNotExist,) as exception:
            raise exception

        except() as exception:
            transaction.rollback()
            raise exception



