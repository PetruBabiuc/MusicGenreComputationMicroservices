import requests
from requests import Response

from config.constants import REQUEST_TIMEOUT
from src.helpers.abstract_classes.AbstractResourceObtainer import AbstractResourceObtainer, T


class SimpleResourceObtainer(AbstractResourceObtainer[Response]):
    def obtain_resource(self, url: str) -> T:
        return requests.get(url, allow_redirects=True, timeout=REQUEST_TIMEOUT)
    