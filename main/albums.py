
from rest_framework import views, viewsets


class AlbumViewSet(viewsets.ModelViewSet):

    serializer_class = serializers.AlbumSerializer
    pass

class AlbumAPIView(views.APIView):
    pass



