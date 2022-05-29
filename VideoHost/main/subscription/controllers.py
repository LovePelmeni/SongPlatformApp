import typing

from rest_framework import generics, mixins, viewsets, decorators, permissions, views
from . import subscription_intergration_api
import django.http


class SubscriptionSerializer(serializers.Serializer):

    subscription_name = serializers.CharField()
    amount = serializers.IntegerField()


class SubscriptionApplyController(subscription_intergration_api.ApplySubscriptionInterface, views.APIView):

    status: typing.Literal["open", "close"]

    def __new__(cls, **kwargs):
        cls.status = "close"
        return super().__new__(**kwargs)

    def handle_exception(self, exc):

        if isinstance(exc, NotImplementedError):
            return django.http.HttpResponseServerError()

    def get_authenticators(self):
        return (authentication.UserAuthenticationClass,)

    def get_permissions(self):
        return (permissions.NOT,) if self.status == 'open' else (permissions.IsAuthenticated,)

    @csrf.requires_csrf_token
    def post(self, request):
        try:
            subscription_model = subscription_intergration_api.SubscriptionDataSchema(request.data)
            self.apply_new_subscription(params=request.query_params, data=subscription_model.dict())
            return django.http.HttpResponse(status=status.HTTP_200_OK)
        except():
            raise NotImplementedError()


class SubscriptionModelGetterAPIView(subscription_intergration_api.GetterSubscriptionInterface, views.APIView):

    def get_permissions(self):
        return (permissions.IsAuthenticated,)

    def get_authenticators(self):
        return (authentication.UserAuthenticationClass,)

    def check_permissions(self, request):
        return self.get_authenticators()[0].authenticate(request)

    @decorators.action(methods=['get'], detail=True)
    def retrieve(self, request):
        subscription = self.get_subscription(sub_id=request.query_params.get('sub_id'))
        return django.http.HttpResponse(subscription, status=200)

    @decorators.action(methods=['get'], detail=False)
    def list(self, request):
        subscriptions = self.get_all_subscriptions(owner_id=request.user.id)
        return django.http.HttpResponse(subscriptions, status=200)



class SubscriptionDocumentController(subscription_intergration_api.PermissionsSubscriptionMixin,
viewsets.ViewSet, subscription_intergration_api.GetterSubscriptionInterface):

    serializer_class = SubscriptionSerializer
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (authentication.AuthenticationClass,)


    @decorators.action(methods=['get'])
    def retrieve(self, request):
        idempotency_key = request.query_params.get('idempotency_key')
        subscription_document = self.get_subscription_document(idempotency_key)
        return django.http.HttpResponse(json.dumps({'document': subscription_document}),
        status=status.HTTP_200_OK, content_type='application/json ')


    @decorators.action(methods=['get'])
    def list(self, request):
        pass

    @decorators.action(methods=['put'])
    def update(self, request):
        pass

    @decorators.action(methods=['delete'])
    def destroy(self, request):
        pass

    @decorators.action(methods=['create'])
    def create(self, request):
        pass


