import json
from unittest.mock import patch
from urllib.parse import urlencode

from django.test import TestCase
from django.urls import reverse

from rest_framework import status

from apps.utils.communication import encode_dict_to_base64
from ..models import User
from .factories import UserFactory
from .utils import RedisMock


class TestUserViewSet(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.redis = RedisMock()
        self.client.force_login(self.user)
        self.user_data = {
            'email': 'webpack@pack.ck',
            'first_name': 'Abraham',
            'last_name': 'Yoba',
            'password': '12345678',
            'password_check': '12345678',
        }
        self.data_without_password = {
            'first_name': 'Abraham',
            'last_name': 'Yoba',
            'email':'webpack@pack.ck'
        }
        self.data = {'time': 3}

    def delay(self, id):
        pass

    def test_create_user(self):
        url = reverse('authentication:user-list')
        response = self.client.post(
            url,
            data=json.dumps(self.user_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get('user').get('email'), self.user_data.get('email'))
        self.assertNotIn('password', response.data.get('user'))
        self.assertTrue(self.user.check_password(self.user_data.get('password')))

    def test_partial_update_user(self):
        data = {
            'first_name': 'New Name',
            'last_name': 'New Last Name',
        }

        url = reverse('authentication:user-detail', args=[self.user.id])
        response = self.client.patch(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('user').get('first_name'), data.get('first_name'))
        self.assertEqual(response.data.get('user').get('last_name'), data.get('last_name'))

    def test_update_user_without_password(self):

        url = reverse('authentication:user-detail', args=[self.user.id])
        response = self.client.put(
            url,
            data=json.dumps(self.data_without_password),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_user_with_password(self):

        url = reverse('authentication:user-detail', args=[self.user.id])
        response = self.client.put(
            url,
            data=json.dumps(self.user_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data.get('password'))
        self.assertTrue('token' in response.data)

    def test_update_password(self):

        password_data = {
            'old_password': '12345678',
            'password': '123456789',
            'password_check': '123456789'
        }
        url = reverse('authentication:user-update-password', args=[self.user.id])
        response = self.client.post(
            url,
            data=json.dumps(password_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get('detail')[0],
            'Password is successfully updated!'
        )
        self.assertTrue(User.objects.get(id=self.user.id).check_password('123456789'))
        self.assertTrue('token' in response.data)

    
    @patch('apps.authentication.views.send_notification_user_created.delay')
    @patch('apps.authentication.serializers.cache.get')
    def test_email_confirmation(self, mocked_redis_get, mocked_task_delay):
        mocked_task_delay.side_effect = self.delay
        mocked_redis_get.side_effect = self.redis.get

        data = {
            'id': self.user.id,
            'uuid': 'qwefmnib82o6vg7i3uj2n92p[3'
        }
        hash_value = urlencode({'hash': encode_dict_to_base64(data)})
        self.redis.set(f'email_confirmation_{self.user.id}', data)
        url = reverse('authentication:user-confirm-email')
        response = self.client.get(
            f'{url}?{hash_value}', content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('is_confirmed_email'), True)
        self.assertTrue(User.objects.get(id=self.user.id).is_confirmed_email)

    @patch('apps.authentication.views.send_password_restore_link.delay')
    def test_restore_password_link(self, mocked_task_delay):
        mocked_task_delay.side_effect = self.delay

        restore_data = {'email': self.user.email}
        url = reverse('authentication:user-restore-password-link')
        response = self.client.post(
            url,
            data=json.dumps(restore_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get('detail')[0],
            'Email is sent!'
        )

        self.assertIsNone(mocked_task_delay.assert_called_once_with(self.user.id))

    def test_restore_password_link_invalid_email(self):
        restore_data = {'email': 'invalid@mail.com'}
        url = reverse('authentication:user-restore-password-link')
        response = self.client.post(
            url,
            data=json.dumps(restore_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data.get('email')[0],
            'Email is invalid'
        )

    @patch('apps.authentication.serializers.cache.get')
    def test_restore_password(self, mocked_redis_get):
        mocked_redis_get.side_effect = self.redis.get

        data = {
            'id': self.user.id,
            'uuid': 'qwefmnib82o6vg7i3uj2n92p[3'
        }
        restore_data = {
            'password': '123456789',
            'password_check': '123456789'
        }
        hash_value = urlencode({'hash': encode_dict_to_base64(data)})
        self.redis.set(f'password_restore_{self.user.id}', data)
        url = reverse('authentication:user-restore-password')
        response = self.client.post(
            f'{url}?{hash_value}',
            data=json.dumps(restore_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(User.objects.get(id=self.user.id).check_password('123456789'))
        self.assertEqual(
            response.data.get('detail')[0],
            'Password is successfully restored!'
        )

    @patch('apps.authentication.managers.UserManager.create')
    def test_create_user_use_proper_manager_method(self, mocked_create):
        mocked_create.return_value = self.user
        response = self.client.post(
            path=reverse('authentication:user-list'),
            data=json.dumps(self.user_data),
            content_type='application/json'
        )

        # we don't have password_check in response
        self.user_data.pop('password_check', None)
        expect_kwargs = set(self.user_data)
        call_kwargs = set(mocked_create.call_args[1])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
