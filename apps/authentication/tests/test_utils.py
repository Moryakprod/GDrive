from django.test import TestCase

from .utils import RedisMock


class TestRedisMock(TestCase):
    def setUp(self):
        self.redis = RedisMock()
        self.key = 'key'
        self.value = 'value'

    def test_redis_set(self):
        self.assertIsNone(self.redis.data.get(self.key))
        self.redis.set(self.key, self.value)
        self.assertEqual(self.redis.data.get(self.key), self.value)

    def test_redis_get(self):
        self.assertIsNone(self.redis.get(self.key))
        self.redis.set(self.key, self.value)
        self.assertEqual(self.redis.get(self.key), self.value)

    def test_redis_delete(self):
        self.redis.set(self.key, self.value)
        self.redis.delete(self.key)
        self.assertIsNone(self.redis.get(self.key))
