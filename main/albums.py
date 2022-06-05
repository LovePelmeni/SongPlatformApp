import django.utils.decorators
from rest_framework import views, viewsets, permissions as rest_perms
from . import permissions
import json
import django.http, django.core.serializers.json
from django.views.decorators import vary


class AlbumViewSet(viewsets.ModelViewSet):

    serializer_class = serializers.AlbumSerializer
    permission_classes = (permissions.IsAlbumOwner, rest_perms.IsAuthenticated)
    queryset = models.Album.objects.all()

    @django.utils.decorators.method_decorator(vary.vary_on_headers('Authorization'))
    def retrieve(self, request, *args, **kwargs):
        queryset = self.get_queryset().filter(owner=request.user,
        id=request.query_params.get('album_id')).select_related('songs')
        return django.http.HttpResponse(json.dumps({'queryset': queryset},
        cls=django.core.serializers.json.DjangoJSONEncoder))

    @django.utils.decorators.method_decorator(vary.vary_on_headers('Authorization'))
    def list(self, request, **kwargs):
        queryset = self.get_queryset().filter(owner=request.user)
        return django.http.HttpResponse(json.dumps({'queryset': queryset},
        cls=django.core.serializers.json.DjangoJSONEncoder))


class AlbumAPIView(views.APIView):

    serializer_class = serializers.AlbumSerializer
    permission_classes = (permissions.IsAlbumOwner,
    rest_perms.IsAuthenticated,)


    def handle_exception(self, exc):
        if isinstance(exc, django.core.exceptions.ObjectDoesNotExist):
            return django.http.HttpResponseNotFound()
        return django.http.HttpResponseServerError()


    @cache.cache_page(timeout=60 * 5)
    def get(self, request):
        return django.http.JsonResponse(
        {'form': forms.AlbumForm()})


    @csrf.requires_csrf_token
    def post(self, request):
        album = self.serializer_class(request.data, many=False)
        if album.is_valid(raise_exception=True):
            if 'queryset' in album.validated_data.items():
                album.songs.update(**album.validated_data.get('queryset'))

        logger.debug('data has been obtained..')
        return django.http.HttpResponse(status=200)


    @csrf.requires_csrf_token
    def put(self, request):
        try:
            album = models.Album.objects.get(id=request.query_params.get('album_id'))
            updated_data = self.serializer_class(request.data, many=False).validated_data
            album.update(**updated_data)
            return django.http.HttpResponse(status=200)
        except(django.core.exceptions.ObjectDoesNotExist,):
            raise django.core.exceptions.ObjectDoesNotExist()


