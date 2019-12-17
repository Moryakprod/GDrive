class RedisMock():

    def __init__(self):
        self.data = {}

    def set(self, key, val, timeout=0):
        """
        Mock 'set' method for mocked redis.
        """
        self.data[key] = val

    def get(self, key):
        """
        Mock 'get' method for mocked Redis.
        """
        return self.data.get(key)

    def delete(self, key):
        """
        Mock 'delete' method for mocked Redis.
        """
        self.data.pop(key)
