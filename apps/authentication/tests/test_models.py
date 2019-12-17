from django.test import TestCase

from .factories import UserFactory


class TestUserModel(TestCase):

    def setUp(self):
        self.user = UserFactory()

    def test_get_short_name(self):
        self.assertEqual(self.user.get_short_name(), self.user.first_name)

    def test_get_full_name(self):
        self.assertEqual(
            '{0} {1}'.format(self.user.first_name, self.user.last_name),
            self.user.get_full_name()
        )

    def test_str_method(self):
        self.assertEqual(str(self.user), self.user.get_full_name())
