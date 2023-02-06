import unittest

from requests import Response

import config.database_api as api_paths

import requests


class IdentityManagementTests(unittest.TestCase):
    credentials = {
        'admin': {'user_name': 'admin', 'password': 'admin'},
        'microservice': {'user_name': 'microservice', 'password': 'microservice'},
        'user': {'user_name': 'crawler_user_1', 'password': 'password'},
    }
    LOGIN_PATH = api_paths.API_URL_PREFIX + api_paths.LOGIN_PATH
    VALIDATE_JWT_PATH = api_paths.API_URL_PREFIX + api_paths.VALIDATE_JWT_PATH

    def __authenticate(self, user: str) -> Response:
        return requests.post(self.LOGIN_PATH, json=self.credentials[user])

    def __validate(self, validator_token: str, validated_token: str) -> Response:
        return requests.post(self.VALIDATE_JWT_PATH,
                             json={'jwt': validated_token},
                             headers={'Authorization': f'Bearer {validator_token}'})

    def test_authenticate_admin_ok(self):
        response = self.__authenticate('admin')
        self.assertTrue(response.ok)

    def test_authenticate_microservice_ok(self):
        response = self.__authenticate('microservice')
        self.assertTrue(response.ok)

    def test_validate_jws_ok(self):
        microservice_jwt = self.__authenticate('microservice').json()['jwt']
        admin_jwt = self.__authenticate('admin').json()['jwt']

        r = self.__validate(microservice_jwt, admin_jwt)
        self.assertTrue(r.ok)
        self.assertEqual(r.json()['status'], 'valid')

        r = self.__validate('q' + microservice_jwt, admin_jwt)
        self.assertFalse(r.ok)
        self.assertEqual(r.status_code, 403)

        r = self.__validate(microservice_jwt, admin_jwt + 'w')
        self.assertTrue(r.ok)
        self.assertEqual(r.json()['status'], 'invalid')
