import django.core.exceptions
from rest_framework import generics, viewsets, mixins, decorators, status
from . import models, permissions
import django.http
from django.views.decorators import http, cache, csrf
from django.db import transaction


class SongCatalogViewSet(viewsets.ModelViewSet):

    queryset = models.Song.objects.all()

    @decorators.action(methods=['get'], detail=True, description='Obtain Single Song Object.')
    def retrieve(self, request, *args, **kwargs):
        try:
            self.object = models.Song.objects.get(id=request.query_params.get('song_id'))
            return super().retrieve(request, *args, **kwargs)
        except(django.core.exceptions.ObjectDoesNotExist,):
            return django.http.HttpResponseNotFound()

    @decorators.action(methods=['get'], detail=False, description='Obtain Song Queryset.')
    def list(self, request, *args, **kwargs):
        self.queryset = models.Song.objects.all()
        return super().list(request, *args, **kwargs)



class SongOwnerGenericView(generics.GenericAPIView):

    queryset = models.Song.objects.all()
    permissions = (permissions.HasSongPermission,)


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

        except(djagno.core.exceptions.ValidationError,) as exception:
            raise exception

        except(django.core.exceptions.ObjectDoesNotExist,) as exception:
            raise exception

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



