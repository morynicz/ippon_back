from django.contrib.auth.hashers import make_password
from django.http.request import HttpRequest
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

import ippon.serializers as ips


@api_view(['POST'])
def register_user(request):
    """
    Validate input data
    if validation passes it registers the user and returns the sent data
    if validations fails if returns a list of errors in the data
    """

    serializer = ips.UserRegistrationSerializer(data=request.data)
    if serializer.is_valid(raise_exception=False):
        user = serializer.save(password=make_password(serializer.validated_data["password"]))
        user.email_user(
            subject="You have been registered",
            message=f"You have been successfully registered in ippon with username {user.username}")
        return Response(status=status.HTTP_201_CREATED, data=serializer.data, content_type="application/json")
    else:
        response = [str(err[0]) for err in serializer.errors.values()]
        return Response(status=status.HTTP_400_BAD_REQUEST, data=response, content_type="application/json")


@api_view(["get"])
def user_data(request: HttpRequest):
    """
    Endpoint for returning basic data about the user currently:
    id, first_name, last_name, username and email
    """
    user: User = request.user
    if user.is_authenticated:
        return Response({
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username,
            "email": user.email
        })
    return Response(data={"error": "You are not logged in."}, status=status.HTTP_401_UNAUTHORIZED)


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsEventOwnerOrReadOnly]

    def create(self, request: Request, *args, **kwargs) -> Response:
        res = super(EventViewSet, self).create(request, *args, **kwargs)
        admin = EventAdmin(
            user=request.user,
            event=Event.objects.get(pk=res.data['id'])
        )
        admin.save()
        return res

    @action(
        methods=["GET"],
        detail=False,
        url_name='my_tournaments')
    def my_tournaments(self, request: Request):
        if request.user.is_authenticated:
            model = Event.objects.filter(event_owner=request.user.pk)
            return Response(data=self.serializer_class(model, many=True).data)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data={"error": "You are not logged in."})
