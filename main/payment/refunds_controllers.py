from rest_framework import views
from django.views.decorators import csrf


class RefundPaymentView(views.APIView):

    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (authentication.UserAuthenticationClass,)


    @csrf.requires_csrf_token
    def post(self, request):
        pass
