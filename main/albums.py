import typing

import django.utils.decorators
from rest_framework import views, viewsets, permissions as rest_perms
from . import permissions, serializers, models
import json
from django.views.decorators import cache, csrf

import django.http, django.core.serializers.json
from django.views.decorators import vary
from django.db import transaction


class AlbumViewSet(viewsets.ModelViewSet):

    serializer_class = serializers.AlbumSerializer
    permission_classes = (permissions.IsAlbumOwner,)
    queryset = models.Album.objects.all()

    @django.utils.decorators.method_decorator(vary.vary_on_headers('Authorization'))
    def retrieve(self, request, *args, **kwargs):
        queryset = list(self.get_queryset().filter(owner=request.user,
        id=request.query_params.get('album_id')).select_related('songs').values())

        return django.http.HttpResponse(json.dumps({'queryset': queryset},
        cls=django.core.serializers.json.DjangoJSONEncoder), status=status.HTTP_200_OK)


    @django.utils.decorators.method_decorator(vary.vary_on_headers('Authorization'))
    def list(self, request, **kwargs):
        queryset = self.get_queryset().filter(owner=request.user)
        return django.http.HttpResponse(json.dumps({'queryset': queryset},
        cls=django.core.serializers.json.DjangoJSONEncoder))


class AlbumAPIView(views.APIView):

    serializer_class = serializers.AlbumSerializer
    permission_classes = (permissions.IsAlbumOwner,)

    def handle_exception(self, exc):
        if isinstance(exc, django.core.exceptions.ObjectDoesNotExist):
            return django.http.HttpResponseNotFound()
        return django.http.HttpResponseServerError()

    @transaction.atomic
    @csrf.requires_csrf_token
    def post(self, request):
        try:
            album = self.serializer_class(request.data, many=False)
            if album.is_valid(raise_exception=True):
                if 'queryset' in album.validated_data.items():
                    album.songs.update(**album.validated_data.get('queryset'))

            logger.debug('data has been obtained..')
            return django.http.HttpResponse(status=200)
        except() as exception:
            transaction.rollback()
            raise exception

    @transaction.atomic
    @csrf.requires_csrf_token
    def put(self, request):
        try:
            album = models.Album.objects.get(id=request.query_params.get('album_id'))
            updated_data = self.serializer_class(request.data, many=False).validated_data
            album.update(**updated_data)
            return django.http.HttpResponse(status=200)

        except(django.core.exceptions.ObjectDoesNotExist,):
            transaction.rollback()
            raise django.core.exceptions.ObjectDoesNotExist()


