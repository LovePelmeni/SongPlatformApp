import django.utils.decorators
from rest_framework import generics, status, authentication, permissions
from django.views.decorators import csrf
from . import models
import django.db.models


class SubscriptionSongGenericView(generics.GenericAPIView):

    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (authentication.UserAuthenticationClass,)
    queryset = models.Song.object.all()

    def handle_exception(self, exc):

        if isinstance(exc, django.core.exceptions.PermissionDenied):
            return django.http.HttpResponse(status=status.HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS)

        if isinstance(exc, django.db.IntegrityError) or isinstance(exc, django.db.ProgrammingError):
            return django.http.HttpResponseServerError()


    @csrf.requires_csrf_token
    def post(self, request):
        subscription = request.data.get('sub_id')
        chosen_songs = django.db.models.QuerySet(model=models.Song,
        query=request.data.get('queryset'))

        for song in chosen_songs:
            song.subscriptions.append(subscription)

        updated = self.get_queryset().bulk_update(fields=['subscriptions'], objs=chosen_songs)
        return django.http.HttpResponse({'updated_songs': updated})


    @django.utils.decorators.method_decorator(cache.never_cache)
    def get(self, request):
        queryset = (query for query in self.get_queryset() if request.user in query.owners.all())
        permission_form = forms.SetPermissionForm()
        permission_form.songs.update({'queryset': queryset})
        return django.http.HttpResponse({'form': permission_form}, status=status.HTTP_200_OK)

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
            raise exception


