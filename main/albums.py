import abc
import typing

import django.utils.decorators
from rest_framework import views, viewsets, permissions as rest_perms

from . import permissions, serializers, models
import json

from django.views.decorators import cache, csrf
import django.http, django.core.serializers.json

from django.views.decorators import vary
from django.db import transaction
from rest_framework import permissions as api_perms

from . import authentication
from rest_framework import decorators


class AlbumViewSet(viewsets.ModelViewSet):

    serializer_class = serializers.AlbumSerializer
    permission_classes = (permissions.IsAlbumOwner, api_perms.IsAuthenticated,)
    authentication_classes = (authentication.UserAuthenticationClass,)
    queryset = models.Album.objects.all()


    @django.utils.decorators.method_decorator(vary.vary_on_headers('Authorization'))
    @decorators.action(methods=['get'], detail=True)
    def retrieve(self, request, *args, **kwargs):
        queryset = list(self.get_queryset().filter(owner=request.user,
        id=request.query_params.get('album_id')).select_related('songs').values())

        return django.http.HttpResponse(json.dumps({'queryset': queryset},
        cls=django.core.serializers.json.DjangoJSONEncoder), status=status.HTTP_200_OK)


    @django.utils.decorators.method_decorator(vary.vary_on_headers('Authorization'))
    @decorators.action(methods=['get'], detail=False)
    def list(self, request, **kwargs):
        queryset = self.get_queryset().filter(owner=request.user)
        return django.http.HttpResponse(json.dumps({'queryset': queryset},
        cls=django.core.serializers.json.DjangoJSONEncoder))


from rest_framework import authentication
from . import authentication as auth

class AlbumAPIView(views.APIView):

    permission_classes = (permissions.IsAlbumOwner, rest_perms.IsAuthenticated,)
    authentication_classes = (auth.UserAuthenticationClass,)

    def handle_exception(self, exc):
        if isinstance(exc, django.core.exceptions.ObjectDoesNotExist):
            return django.http.HttpResponseNotFound()
        return django.http.HttpResponseServerError()

    @transaction.atomic
    @csrf.csrf_exempt
    def post(self, request):
        try:
            album = serializers.SongCreateSerializer(data=request.data, many=False)
            if album.is_valid(raise_exception=True):
                if 'queryset' in album.validated_data.items():
                    album.songs.bulk_create(album.validated_data.get('queryset'))

            logger.debug('data has been obtained..')
            return django.http.HttpResponse(status=200)
        except() as exception:
            transaction.rollback()
            raise exception

    @transaction.atomic
    @csrf.csrf_exempt
    def put(self, request):
        try:
            album = models.Album.objects.get(id=request.query_params.get('album_id'))
            updated_data = serializers.SongUpdateSerializer(data=request.data,
            many=False).validated_data
            album.update(**updated_data)
            return django.http.HttpResponse(status=200)

        except(django.core.exceptions.ObjectDoesNotExist,):
            transaction.rollback()
            raise django.core.exceptions.ObjectDoesNotExist()


