import django.utils.decorators
from rest_framework import generics, status, authentication, permissions, viewsets

from django.views.decorators import csrf, cache
import django.http
from . import authentication as api_auth

from . import models, forms, authentication as auth
import django.db.models
from django.db import transaction


def cache_subscriptions(subscriptions):
    from django.core.cache import cache
    return cache.set('')

class SubscriptionGenericView(generics.GenericAPIView):

    queryset = models.Subscription.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (auth.UserAuthenticationClass,)

    def handle_exception(self, exc):
        if isinstance(exc, django.core.exceptions.ObjectDoesNotExist):
            return django.http.HttpResponseNotFound()

    @transaction.atomic
    @csrf.requires_csrf_token
    def post(self, request):
        try:
            from . import aws_s3
            serializer = serializers.SubscriptionSerializer(request.data, many=False)

            if 'preview' in request.FILES.keys():
                file_link = aws_s3.files_api._save_to_aws(bucket_name=getattr(
                settings, 'BUCKET_PREVIEW_NAME'), file=request.FILES.get('preview'))
                serializer.validated_data.update({'preview': file_link})

            if serializer.is_valid(raise_exception=True):
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
                # file_link = aws_s3.files_api._save_to_aws(bucket_name=getattr(
                #
                # settings, 'BUCKET_PREVIEW_NAME'), file=request.FILES.get('preview'))
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

    @cache.cache_page(timeout=60 * 5)
    def get(self, request):
        form = forms.SubscriptionForm()
        return django.http.HttpResponse(
        json.dumps({'form': form}), status=200)


class SubscriptionSongGenericView(generics.GenericAPIView):

    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (api_auth.UserAuthenticationClass,)
    queryset = models.Song.objects.all()

    def handle_exception(self, exc):

        if isinstance(exc, django.core.exceptions.PermissionDenied):
            return django.http.HttpResponse(status=status.HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS)

        if isinstance(exc, django.db.IntegrityError) or isinstance(exc, django.db.ProgrammingError):
            return django.http.HttpResponseServerError()

    @transaction.atomic
    @csrf.requires_csrf_token
    def post(self, request):
        try:
            subscription = request.data.get('subscription_id')
            chosen_songs = django.db.models.QuerySet(model=models.Song,
            query=request.data.get('queryset'))

            for song in chosen_songs:
                song.subscriptions.append(subscription)

            updated = self.get_queryset().bulk_update(fields=['subscriptions'], objs=chosen_songs)
            return django.http.HttpResponse({'updated_songs': updated})

        except(django.db.IntegrityError, django.db.ProgrammingError, django.db.OperationalError,) as exception:
            transaction.rollback()
            raise exception

    @django.utils.decorators.method_decorator(cache.never_cache)
    def get(self, request):
        from . import forms
        queryset = [query for query in self.get_queryset() if request.user in query.owners.all()]
        permission_form = forms.SetSubscriptionForm()
        permission_form.songs.update({'queryset': queryset})
        return django.http.HttpResponse({'form': permission_form}, status=status.HTTP_200_OK)

    @transaction.atomic
    @csrf.requires_csrf_token
    def delete(self, request):
        try:
            subscription = request.data.get('subscription')
            chosen_songs = django.db.models.QuerySet(model=models.Song,
            query=request.data.get('queryset'))

            for song in chosen_songs:
                song.subscriptions.append(subscription)

            updated = self.get_queryset().bulk_update(fields=['subscriptions'], objs=chosen_songs)
            return django.http.HttpResponse({'updated_songs': updated})

        except(django.db.IntegrityError, django.db.ProgrammingError,) as exception:
            transaction.rollback()
            raise exception


