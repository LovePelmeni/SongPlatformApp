from django.urls import path
from . import users
from rest_framework import permissions
from . import songs, subscriptions, albums
import django.http

app_name = 'main'

urlpatterns = []

songs_urlpatterns = [

    path('top/week/songs/', songs.TopWeekSongsAPIView.as_view(), name='top-week-songs'),
    path('song/', songs.SongOwnerGenericView.as_view(), name='song'),

    path('get/songs/', songs.SongCatalogViewSet.as_view({'get': 'list'}), name='all-songs'),
    path('get/song/', songs.SongCatalogViewSet.as_view({'get': 'retrieve'}), name='get-song'),

]
subscription_urlpatterns = [

    path('/subscription/', subscriptions.SubscriptionGenericView.as_view(), name='subscription'),
    path('/subscription/song/', subscriptions.SubscriptionSongGenericView.as_view(), name='subscription-song')

]
album_urlpatterns = [

    path('album/', albums.AlbumAPIView.as_view(), name='album'),
    path('get/album/', albums.AlbumViewSet.as_view({'get': 'retrieve'}), name='get-album'),
    path('get/albums/', albums.AlbumViewSet.as_view({'get': 'list'}), name='get-albums'),
]

customer_patterns = [

    #customer urls:
    path('delete/user/', users.delete_user, name='delete-user'),
    path('edit/user/', users.EditUserAPIView.as_view(), name='edit-user'),

    path('create/user/', users.CreateUserAPIView.as_view(), name='create-user'),
    path('login/user/', users.LoginAPIView.as_view(), name='login-user'),
    path('get/user/profile/', users.CustomerProfileAPIView.as_view(), name='get_user_profile'),
]

healthcheck_patterns = [
    path('healthcheck/', (lambda request: django.http.HttpResponse(status=200)), name='healthcheck'),
]


urlpatterns += customer_patterns
urlpatterns += songs_urlpatterns
urlpatterns += subscription_urlpatterns
urlpatterns += album_urlpatterns
urlpatterns += healthcheck_patterns


from drf_yasg import openapi
from drf_yasg.views import get_schema_view

schema_view = get_schema_view(
    openapi.Info(
    title='Web APP',
    default_version='1.0',
    description='API Web App.',
    contact=openapi.Contact(email='kirklimushin@gmail.com'),
    license=openapi.License(name='BSD License')
    ),
    public=True,
    permission_classes = (permissions.AllowAny,)
)
openapi_urlpatterns_schema = [

    path('swagger/json', schema_view.without_ui(cache_timeout=0), name='swagger-schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-schema-ui'),
    path('swagger/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='swagger-schema-redoc')
]

urlpatterns += openapi_urlpatterns_schema





