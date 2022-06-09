import django.utils.decorators
from rest_framework import generics, status, authentication, permissions, viewsets
from django.conf import settings

from django.views.decorators import csrf, cache
import django.http
from . import authentication as api_auth, serializers

from . import models, authentication as auth, dropbox as dropbox_storage
import django.db.models
from django.db import transaction
import logging

logger = logging.getLogger(__name__)


class SubscriptionGenericView(generics.GenericAPIView):

    queryset = models.Subscription.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (auth.UserAuthenticationClass,)

    dropbox_storage = dropbox_storage.files_api.DropBoxBucket(
    getattr(settings, 'DROPBOX_SUBSCRIPTION_PREVIEW_FILE_PATH'))

    def handle_exception(self, exc):
        if isinstance(exc, django.core.exceptions.ObjectDoesNotExist):
            return django.http.HttpResponseNotFound()

    @transaction.atomic
    @csrf.requires_csrf_token
    def post(self, request):
        try:
            from . import dropbox
            serializer = serializers.SubscriptionSerializer(request.data, many=False)
            if serializer.is_valid(raise_exception=True):

                if 'preview' in request.FILES.keys():
                    preview = request.FILES.get('preview')

                    file_link = self.dropbox_storage.upload(file=request.FILES.get('preview'),
                    filename=preview.name.split('.')[0])
                    serializer.validated_data.update({'preview': file_link})

            models.Subscription.objects.create(
            **serializer.validated_data)

            logger.debug('new subscription has been created.')
            return django.http.HttpResponse(status=status.HTTP_200_OK)

        except(django.db.IntegrityError,) as exception:
            transaction.rollback()
            raise exception

    @transaction.atomic
    @csrf.requires_csrf_token
    def put(self, request):
        try:
            subscription = models.Subscription.objects.get(id=request.query_params.get('subscription_id'))
            serializer = serializers.SubscriptionSerializer(request.data, many=False)

            if 'preview' in serializer.validated_data.keys():
                file_link = self.dropbox_storage.upload(file=request.FILES.get('preview'),
                filename=request.FILES.get('preview').name.split('.')[0])
                serializer.validated_data.update({'preview': file_link})

            if serializer.is_valid(raise_exception=True):
                for obj, value in serializer.validated_data.items():
                    subscription.__setattr__(obj, value)

            return django.http.HttpResponse(status=status.HTTP_200_OK)
        except(django.db.IntegrityError, django.core.exceptions.ObjectDoesNotExist,) as exception:
            transaction.rollback()
            raise exception

    @transaction.atomic
    @csrf.requires_csrf_token
    def delete(self, request):
        try:
            subscription_id = request.query_params.get('subscription_id')
            models.Subscription.objects.delete(subscription_id=subscription_id)
            return django.http.HttpResponse(status=status.HTTP_200_OK)

        except(django.core.exceptions.ObjectDoesNotExist,) as exception:
            transaction.rollback()
            raise exception


class SubscriptionSongGenericView(generics.GenericAPIView):

    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (api_auth.UserAuthenticationClass,)
    queryset = models.Song.objects.all()

    def handle_exception(self, exc):

        if isinstance(exc, django.core.exceptions.PermissionDenied):
            return django.http.HttpResponse(status=status.HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS)

        if isinstance(exc, django.db.IntegrityError) or isinstance(exc, django.db.ProgrammingError):
            return django.http.HttpResponseServerError()

        return django.http.HttpResponseServerError()

    @transaction.atomic
    @csrf.requires_csrf_token
    def post(self, request):
        try:
            subscription = models.Subscription.objects.get(id=request.data.get('subscription_id'))
            chosen_songs = request.data.get('queryset')

            subscription.songs.bulk_create(
            [Song(**song) for song in chosen_songs]
            )
            return django.http.HttpResponse({'updated_songs': updated})

        except(django.db.IntegrityError, django.db.ProgrammingError, django.db.OperationalError,) as exception:
            transaction.rollback()
            raise exception

    @transaction.atomic
    @csrf.requires_csrf_token
    def delete(self, request):
        try:
            song = self.get_queryset().filter(id=request.query_params.get('song_id'))
            subscription = request.data.get('subscription')
            subscription.songs.delete(id=song.id)
            return django.http.HttpResponse({'updated_songs': updated})

        except(django.db.IntegrityError, django.db.ProgrammingError,
        django.core.exceptions.ObjectDoesNotExist,) as exception:
            transaction.rollback()
            raise exception

