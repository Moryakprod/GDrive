from unittest.mock import patch

from django.test import TestCase

from apps.utils.communication import encode_dict_to_base64
from .factories import UserFactory
from .utils import RedisMock
from ..serializers import BasePasswordSerializer, HashSerializer, UpdatePasswordSerializer, \
    UserSerializer


class TestUserSerializer(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.user_data = {
            'first_nam': 'Abraham',
            'last_name': 'Yoba',
            'emai': 'webpack@pack.c',
            'password': 'qwerty123',
        }

    def test_get_valid_user_fields(self):
        serializer = UserSerializer(self.user)
        self.assertEqual(serializer.data.get('email'), self.user.email)
        self.assertEqual(serializer.data.get('id'), self.user.id)
        # we mustn't serialize and send password!
        self.assertIsNone(serializer.data.get('password'))


class TestPasswordSerializer(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.redis = RedisMock()

    def test_update_password_serializer(self):
        update_pass_data = {
            'old_password': '12345678',
            'password': '123456789',
            'password_check': '123456789'
        }
        serializer = UpdatePasswordSerializer(data=update_pass_data, context=self.user)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(
            serializer.data.get('password'),
            update_pass_data.get('password')
        )

    def test_validate_wrong_old_password(self):
        wrong_old_pass = {
            'old_password': '11111111',
            'password': '123456789',
            'password_check': '123456789'
        }
        serializer = UpdatePasswordSerializer(data=wrong_old_pass, context=self.user)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            str(serializer.errors.get('old_password')[0]),
            'Current password is incorrect'
        )

    def test_validate_old_password_matching_new_one(self):
        same_pass = {
            'old_password': '12345678',
            'password': '12345678',
            'password_check': '12345678'
        }
        serializer = UpdatePasswordSerializer(data=same_pass, context=self.user)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            str(serializer.errors.get('old_password')[0]),
            'New password cannot be the same as your old password'
        )

    def test_validate_not_matching_passwords(self):
        not_matching_pass = {
            'password': '123456789',
            'password_check': '12345678910'
        }
        serializer = BasePasswordSerializer(data=not_matching_pass)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            str(serializer.errors.get('password_check')[0]),
            "Passwords don't match!"
        )

    
    @patch('apps.authentication.serializers.cache.delete')
    @patch('apps.authentication.serializers.cache.get')
    def test_hash_validation(self, mocked_redis_get, mocked_redis_delete):
        mocked_redis_get.side_effect = self.redis.get
        mocked_redis_delete.side_effect = self.redis.delete

        data = {
            'id': self.user.id,
            'uuid': 'qwefmnib82o6vg7i3uj2n92p[3'
        }
        self.assertEqual(self.redis.data, {})
        self.redis.set(f'email_confirmation_{self.user.id}', data)
        self.assertNotEqual(self.redis.data, {})
        hash_data = {'hash': encode_dict_to_base64(data)}
        serializer = HashSerializer(data=hash_data, cache_key_action='email_confirmation_')
        self.assertTrue(serializer.is_valid())
        self.assertEqual(self.redis.data, {})

    @patch('apps.authentication.serializers.cache.get')
    def test_redis_calling(self, mocked_redis_get):
        mocked_redis_get.side_effect = self.redis.get

        data = {
            'id': self.user.id,
            'uuid': 'qwefmnib82o6vg7i3uj2n92p[3'
        }
        calling_arg = f'email_confirmation_{self.user.id}'
        self.redis.set(calling_arg, data)
        hash_data = {'hash': encode_dict_to_base64(data)}
        serializer = HashSerializer(data=hash_data, cache_key_action='email_confirmation_')
        self.assertTrue(serializer.is_valid())

        mocked_redis_get.assert_called_with(calling_arg)
