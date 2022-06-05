import django.core.exceptions
from rest_framework import generics, viewsets, mixins, decorators, status, permissions

from . import models, authentication, permissions as api_permissions
import django.http

from django.views.decorators import http, cache, csrf
from django.db import transaction


class SongCatalogViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = models.Song.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (authentication.UserAuthenticationClass,)


    def handle_exception(self, exc):
        if isinstance(exc, django.core.exceptions.PermissionDenied):
            return django.http.HttpResponse(status=status.HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS)

        if isinstance(exc, django.core.exceptions.ObjectDoesNotExist):
            return django.core.exceptions.ObjectDoesNotExist
        return django.http.HttpResponseServerError()


    def check_object_permissions(self, request, song):
        if not song in request.user.songs.all() \
        or not song.subscrition in request.user.subscriptions.all():
            raise django.core.exceptions.PermissionDenied()

    def get_queryset(self):
        return self.filter_queryset(queryset=self.queryset)


    @decorators.action(methods=['get'], detail=True, description='Obtain Single Song Object.')
    def retrieve(self, request, *args, **kwargs):
        try:
            song = models.Song.objects.get(id=request.query_params.get('song_id'))
            self.check_object_permissions(request=request, song=song)
            return super().retrieve(request, *args, **kwargs)

        except(django.core.exceptions.ObjectDoesNotExist,):
            return django.http.HttpResponseNotFound()

        except(django.core.exceptions.PermissionDenied,):
            return django.http.JsonResponse({'is_available': False})


    @decorators.action(methods=['get'], detail=False, description='Obtain Song Queryset.')
    def list(self, request, *args, **kwargs):

        from django.db import models as db_models
        self.queryset = self.get_queryset().annotate(is_available=db_models.Case(
        db_models.When(subscription__in=request.user.subscriptions.all(), then=True),

        db_models.When(~db_models.Q(subscription__in=request.user.subscriptions.all()), then=False),
        output_field=django.db.models.BooleanField()))
        return super().list(request, *args, **kwargs)

    def filter_queryset(self, queryset):
        return queryset.filter(len(F('subscriptions')) < 1)


import typing
class TopWeekSongsAPIView(generics.GenericAPIView):

    permission_classes = (permissions.AllowAny,)
    queryset = models.Song.objects.all()

    def get_most_viewed_queryset(self) -> typing.List[dict]:
        """
        / * returns most listened songs during this week.
        // * joins with Song queryset by song ID.
        """
        from django.db import models as db_models
        # query = [query for query in self.get_queryset().select_related('statistic').order_by('-views')[:10]]
        general_query = self.get_queryset().raw('SELECT * FROM main_song JOIN'
        # / * join implementation between Song and their statistic
        'SELECT * FROM main_statsong ORDER BY views DESC LIMIT 10 ON main_song.id=main_statsong.id').annotate(
        views_count=db_models.F('views')).order_by('-views')[:10]
        return general_query

    @cache.cache_page(timeout=60 * 5)
    def get(self, request):
        parsed_queryset = self.get_most_viewed_queryset()
        return django.http.HttpResponse(
        data=json.dumps({'queryset': parsed_queryset.values()},
        cls=django.core.serializers.json.DjangoJSONEncoder), status=200)


class SongOwnerGenericView(generics.GenericAPIView):

    queryset = models.Song.objects.all()
    permissions = (api_permissions.HasSongPermission,)


    def get_song_etag(self, request):
        return self.get_queryset().filter(
        id=request.query_params.get('song_id')).first().etag


    def handle_exception(self, exc):

        if isinstance(exc, django.core.exceptions.ValidationError):
            return django.http.HttpResponseBadRequest()

        if isinstance(exc, django.core.exceptions.ObjectDoesNotExist):
            return django.http.HttpResponseNotFound()

        if isinstance(exc, django.core.exceptions.PermissionDenied):
            return django.http.HttpResponse(status=status.HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS)


    @cache.cache_page(timeout=60 * 5)
    def get(self, request):
        try:
            song = self.get_queryset().get(id=request.query_params.get('song_id'))
            return django.http.JsonResponse(
            {'form': forms.SongForm(initial={elem: getattr(song, elem)
            for elem, value in song._meta.get_fields()})})

        except(django.core.exceptions.ObjectDoesNotExist,) as exception:
            raise exception

    @transaction.atomic
    @http.etag(etag_func=get_song_etag)
    @csrf.requires_csrf_token
    def put(self, request):
        try:
            song = self.get_queryset().get(id=request.query_params.get('song_id'))
            serializer = serializers.SongUpdateSerializer(request.data, many=False)

            if serializers.is_valid(raise_exception=True):
                if 'preview' in request.FILES.keys():

                    file_link = aws_s3.files_api._save_to_aws(
                    bucket_name=getattr(settings, 'SONG_AUDIO_BUCKET_NAME'), file=request.FILES.get('preview'))
                    serializer.validated_data.update({'preview': file_link})

                for elem, value in serializer.validated_data.items():
                    song.__setattr__(elem, value)

                song.save()
                return django.http.HttpResponse(status=200)

        except() as exception:
            transaction.rollback()
            raise exception

    @transaction.atomic
    @csrf.requires_csrf_token
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

