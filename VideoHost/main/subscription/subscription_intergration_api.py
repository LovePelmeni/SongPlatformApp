import requests, pydantic
from rest_framework import views
import django.core.exceptions


class SubscriptionDataSchema(pydantic.BaseModel):

    subscription_id: int
    subscription_name: str
    owner_id: int
    amount: int
    purchaser_id: int

class PermissionsSubscriptionMixin(object):

    def check_permissions(self, request):
        import requests
        permissions_api_url = 'http://localhost:8076/check/sub/permission/'
        request_http_params = {'customer_id': request.user.id}
        response = requests.get(permissions_api_url, params=request_http_params, timeout=10)
        if not json.loads(response.text).get('sub_property'):
            raise django.core.exceptions.PermissionDenied()

    def __init__(self):
        permissions_method = getattr(self, 'check_permissions', None)
        if callable(permissions_method):
            self.check_permissions = self.check_permissions


class GetterSubscriptionInterface(object):

    def get_subscription(self, sub_id):
        pass

    def get_all_subscriptions(self, owner_id):
        pass


class ApplySubscriptionInterface(object):

    def block_incoming_requests(self):
        self.status = 'open'

    def apply_new_subscription(self, params, data):
        try:
            response = requests.post('http://localhost:8077/activate/sub/',
            params=params, data=data, timeout=20)
        except():
            pass


