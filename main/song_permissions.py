from rest_framework import viewsets, decorators
from . import permissions

class SongPermissions(viewsets.ModelViewSet):

    permission_classes = (permissions.HasSongPermission,)

    def handle_exception(self, exception):
        return django.http.HttpResponseNotFound() if exception.__class__.__name__ in (
        django.core.exceptions.ObjectDoesNotExist.__class__.__name__, AttributeError.__class__.__name__) else \
        django.http.HttpResponseServerError()

    @decorators.action(methods=['post'], detail=False)
    def create(self, request):
        try:
            song = models.Song.objects.filter(id=request.query_params.get('song_id')).first()
            user = models.APICustomer.objects.get(id=request.query_params.get('customer_id'))
            song.owners.add(user)
            return django.http.HttpResponse(status=200)
        except(django.core.exceptions.ObjectDoesNotExist, AttributeError,) as exception:
            raise exception

    @decorators.action(methods=['delete'], detail=False)
    def destroy(self, request,):
        try:
            song = models.Song.objects.filter(id=request.query_params.get('song_id')).first()
            user = models.APICustomer.objects.get(id=request.query_params.get('customer_id'))
            song.owners.remove(user)
            return django.http.HttpResponse(status=200)
        except(django.core.exceptions.ObjectDoesNotExist, AttributeError,) as exception:
            raise exception




