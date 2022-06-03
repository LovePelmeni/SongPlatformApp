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


    def get_queryset(self):
        return self.filter_queryset(queryset=self.queryset)

    @decorators.action(methods=['get'], detail=True, description='Obtain Single Song Object.')
    def retrieve(self, request, *args, **kwargs):
        try:
            self.object = self.get_queryset().get(id=request.query_params.get('song_id'))
            return super().retrieve(request, *args, **kwargs)
        except(django.core.exceptions.ObjectDoesNotExist,):
            return django.http.HttpResponseNotFound()

    @decorators.action(methods=['get'], detail=False, description='Obtain Song Queryset.')
    def list(self, request, *args, **kwargs):
        self.queryset = self.get_queryset()
        return super().list(request, *args, **kwargs)

    def filter_queryset(self, queryset):
        return queryset.filter(len(F('subscriptions')) < 1)


    @decorators.permission_classes([api_permissions.HasSongPermission,])
    @decorators.action(methods=['get'], detail=True)
    def paid_retrieve(self, request):
        import django.core.serializers.json
        song = models.Song.objects.filter(has_subscription=True, id=request.query_params.get('song_id')).first()
        return django.http.HttpResponse(status=200, content=json.dumps({'song': song.values()},
        cls=django.core.serializers.json.DjangoJSONEncoder), content_type='application/json')


    @decorators.permission_classes([api_permissions.HasSongPermission,])
    @decorators.action(methods=['get'], detail=False)
    def paid_list(self, request):
        queryset = self.get_queryset() + models.Song.objects.filter(has_subscription=True)
        return django.http.HttpResponse(json.dumps({'queryset': queryset},
        cls=django.core.serializers.DjangoJSONEncoder), status=200)


class TopWeekSongsAPIView(generics.GenericAPIView):

    permission_classes = (permissions.AllowAny,)
    queryset = models.Song.objects.all()

    def get_most_viewed_queryset(self) -> typing.List[dict]:
        """
        / * returns most listened songs during this week.
        // * joins with Song queryset by song ID.
        """
        from django.db import models as db_models
        general_query = self.get_queryset().raw('SELECT * FROM Song JOIN '
        # / * join implementation between Song and their statistic
        'SELECT * FROM StatSong ORDER BY views DESC LIMIT 10 ON Song.id=StatSong.id').annotate(
        views_count=db_models.F('views')).order_by('-views_count')[:10]
        return db_models.QuerySet(general_query)

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
                return django.http.HttpResponse()

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



