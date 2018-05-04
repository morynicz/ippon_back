import os

from django.http import JsonResponse
# Create your views here.
from rest_framework_simplejwt.views import TokenObtainPairView

from auth_server.serializers import UserTokenSerializer


def view_pubkey(request):
    return JsonResponse({'key': os.environ['SECRET_KEY_PUBLIC']}, safe=False)


class UserTokenObtainPairView(TokenObtainPairView):
    serializer_class = UserTokenSerializer
