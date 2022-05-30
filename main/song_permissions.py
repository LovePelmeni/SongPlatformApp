from rest_framework import viewsets, decorators, permissions

class SongPermissions(viewsets.ModelViewSet):

    permission_classes = (permissions.AllowAny,)

    @decorators.action(methods=['post'], detail=False)
    def create(self, request):
        try:
            song = models.Song.objects.filter(id=request.query_params.get('song_id')).first()
            user = models.APICustomer.objects.get(id=request.query_params.get('customer_id'))
            song.owners.add(user)
            return django.http.HttpResponse(status=200)
        except(django.core.exceptions.ObjectDoesNotExist, AttributeError,) as excepiton:
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

