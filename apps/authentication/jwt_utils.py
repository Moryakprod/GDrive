from django.utils.translation import ugettext_lazy as _

from rest_framework_jwt.utils import jwt_encode_handler, jwt_payload_handler

from .serializers import UserSerializer


def jwt_response_payload_handler(token, user=None, request=None):
    data = {
        'token': token,
        'user': UserSerializer(user, context={'request': request}).data
    }
    return data


def create_token(user):
    """Create token by user instanse."""
    payload = jwt_payload_handler(user)
    token = jwt_encode_handler(payload)
    return token


def response_with_token(instance, serializer_data):
    """Create response user data with token."""
    token = create_token(instance)
    response = {
        'token': token,
        'user': serializer_data
    }
    return response
