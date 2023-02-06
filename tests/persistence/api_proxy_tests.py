import unittest

from src.helpers.DatabaseApiProxy import DatabaseApiProxy


class ApiProxyTests(unittest.TestCase):
    credentials = {
        'admin': ('admin', 'admin'),
        'microservice': ('microservice', 'microservice'),
        'user': ('crawler_user_1', 'password')
    }

    def test_get_users(self):
        proxy = DatabaseApiProxy('admin', 'admin')
        users = proxy.get_users()
        self.assertTrue(len(users) > 0)
