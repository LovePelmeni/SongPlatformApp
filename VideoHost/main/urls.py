from . import views
from django.urls import path
from . import validators, groups, users, videos
from rest_framework import permissions

app_name = 'main'

urlpatterns = [

]
videos_patterns = [

    path('', views.MainAPIView.as_view(), name='main_page'),
    path('get/all/group/videos/', videos.GroupVideoAPIView.as_view({'action': 'list'}), name='all-videos'),
    path('get/video/', videos.GroupVideoAPIView.as_view({'action': 'retrieve'}), name='video'),
    path('delete/video/', videos.GroupVideoAPIView.as_view({'action': 'delete'}), name='delete-video'),
    path('upload/video/', videos.GroupVideoAPIView.as_view({'action': 'create'}), name='upload-video'),

]

validator_patterns = [

    #validator urls:
    path('validate/register/form/', validators.validate_login_form, name='register-form'),
    path('validate/login/form/', validators.validate_register_form, name='login-form'),
    path('validate/chat/form', validators.validate_chat_form, name='chat-form'),

]

group_patterns = [

    #group urls:
    path('get/group/', groups.GetGroupAPIView.as_view(), name='group'),
    path('create/group/', groups.CreateGroupAPIView.as_view(), name='create-group'),
    path('edit/group/', groups.EditGroupAPIView.as_view(), name='edit-group'),
    path('delete/group/', groups.DeleteGroupAPIView.as_view(), name='delete-group'),

    # members urls:
    path('remove/member/', groups.MembersViewSet.as_view({'delete': 'destroy'}), name='remove-member'),
    path('add/member/', groups.MembersViewSet.as_view({'post': 'create'}), name='add-member'),

    path('get/group/member/', groups.MembersViewSet.as_view({'get': 'retrieve'}), name='get-group-member'),
    path('get/group/members/', groups.MembersViewSet.as_view({'get': 'list'})),

]

customer_patterns = [

    #customer urls:
    path('delete/user/', users.delete_user, name='delete-user'),
    path('edit/user/', users.EditUserAPIView.as_view(), name='edit-user'),

    path('create/user/', users.CreateUserAPIView.as_view(), name='create-user'),
    path('login/user/', users.login_user, name='login-user'),
    path('get/user/profile/', users.get_user_profile, name='get_user_profile'),
]

block_patterns = [

    #block page:
    path('ban/or/unlock/user/', groups.BanUserAPIView.as_view(), name='ban-or-unlock-user'),
    path('get/blocked/page/', views.get_blocked_page, name='blocked_page'),
]

healthcheck_patterns = [
    path('healthcheck/', views.healthcheck, name='healthcheck'),
]


urlpatterns += group_patterns
urlpatterns += customer_patterns
urlpatterns += validator_patterns
urlpatterns =+ videos_patterns
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
