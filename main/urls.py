from . import views
from django.urls import path
from . import users
from rest_framework import permissions
from . import songs, song_permissions

app_name = 'main'

urlpatterns = []

songs_urlpatterns = [

    path('song/', songs.SongOwnerGenericView.as_view(), name='song'),
    path('catalog/all/songs/', songs.SongCatalogViewSet.as_view({'get': 'list'}), name='all-songs'),
    path('get/song/', songs.SongCatalogViewSet.as_view({'get': 'retrieve'}), name='get-song'),
    path('set/song/permission/', song_permissions.SongPermissions.as_view({'post': 'create'}), name='set-song-permission'),
    path('unset/song/permission/', song_permissions.SongPermissions.as_view({'delete': 'destroy'}), name='unset-song-permission')

]

customer_patterns = [

    #customer urls:
    path('delete/user/', users.delete_user, name='delete-user'),
    path('edit/user/', users.EditUserAPIView.as_view(), name='edit-user'),

    path('create/user/', users.CreateUserAPIView.as_view(), name='create-user'),
    path('login/user/', users.LoginAPIView.as_view(), name='login-user'),
    path('get/user/profile/', users.get_user_profile, name='get_user_profile'),
]

block_patterns = [

    #block page:
    path('get/blocked/page/', views.get_blocked_page, name='blocked_page'),
]

healthcheck_patterns = [
    path('healthcheck/', views.healthcheck, name='healthcheck'),
]


urlpatterns += customer_patterns
urlpatterns += songs_urlpatterns
urlpatterns += block_patterns
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



