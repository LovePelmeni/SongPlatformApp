from rest_framework import views
import requests
from django.middleware import csrf as csrf_protection


class ProcessPaymentIntentView(views.APIView):

    authentication_classes = (
    authentication.UserAuthenticationClass,)

    def get_permissions(self):
        return (permissions.NOT,) if self.process_status in ('open') else (permissions.IsAuthenticated,)

    def get_payment_document(self, request):
        return json.dumps({
            **request.data.items(),
            'purchaser_id': request.user.id,
        })

    @csrf.requires_csrf_token
    def post(self, request):

        payment_intent_url = 'abstract_payment_url'
        session = requests.Session()

        document = self.get_payment_document(request)
        http_response = session.request(method='post', headers={'Access-Control-Allow-Origin': '*',
        'CSRF-Token': csrf_protection.get_token(request), 'Content-Type': 'application/json'},
        data=document, timeout=10, url=payment_intent_url)
        return http_response


class ProcessPaymentView(views.APIView):


    def post(self, request):
        pass

