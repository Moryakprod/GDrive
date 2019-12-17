from unittest.mock import patch

from django.test import TransactionTestCase

from .factories import UserFactory


class TestUserModelTransaction(TransactionTestCase):

    def setUp(self):
        with patch('apps.authentication.models.send_email_confirmation_link') as mocked_send:
            self.user = UserFactory()

    @patch('apps.authentication.models.send_email_confirmation_link')
    def test_save_method_with_new_user(self, mocked_send):
        user = UserFactory()
        self.assertIsNone(mocked_send.delay.assert_called_once_with(user.id))

    @patch('apps.authentication.models.send_email_confirmation_link')
    def test_save_method_with_not_new_user(self, mocked_send):
        # now verify there is no interaction
        with self.assertRaises(AssertionError):
            mocked_send.delay.assert_called_once_with(self.user.id)
