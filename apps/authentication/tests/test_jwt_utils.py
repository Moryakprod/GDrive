from django.test import TestCase

from rest_framework.exceptions import ValidationError

from ..jwt_utils import create_token, response_with_token, jwt_response_payload_handler
from ..serializers import UserSerializer
from .factories import UserFactory


class MockRequest:
    pass


class TestJWTUtils(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.user_data = {
            "first_name": "Abraham",
            "last_name": "Yoba",
            "email": "webpack@pack.ck",
            "phone": "+380698569986",
        }

    def test_response_with_token(self):
        response = response_with_token(self.user, self.user_data)
        self.assertTrue('token' and 'user' in response)
        self.assertDictEqual(self.user_data, response.get('user'))

    def test_jwt_response_payload_handler(self):
        token = create_token(self.user)
        request = MockRequest()
        self.user.is_confirmed_email = True
        self.user.save()
        serialized_user = UserSerializer(self.user).data
        response = jwt_response_payload_handler(token, user=self.user, request=request)
        self.assertTrue('token' and 'user' in response)
        self.assertDictEqual(serialized_user, response.get('user'))
