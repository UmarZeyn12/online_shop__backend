from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from apps.api.serializers import auth


@extend_schema(
    request=auth.UserRegistrationSerializer,
    responses={201: auth.UserRegistrationSerializer},
)
@api_view(["POST"])
def register_user(request):
    serializer = auth.UserRegistrationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)
