from __future__ import annotations

from urllib.parse import urljoin

from config.redis import SPIDER_TOPIC
from src.helpers import Base64Converter
from src.helpers.Mp3ValidatorProxy import Mp3ValidatorProxy
from src.helpers.abstract_classes.AbstractMimeContentProcessor import AbstractMimeContentProcessor
from src.helpers.resource_obtainers.SimpleResourceObtainer import SimpleResourceObtainer


class Mp3Processor(AbstractMimeContentProcessor):
    def __init__(self):
        types = ['audio/mpeg']
        obtainer = SimpleResourceObtainer()
        super().__init__(types, obtainer)
        self.__mp3_validator_proxy = Mp3ValidatorProxy(SPIDER_TOPIC, 'song_url')

    def process_resource(self, resource: str, domain: str) -> tuple[list[str], bool]:
        # TODO: REMOVE
        # return [], True
        # Test if the response's content is an MP3
        resource = urljoin(domain, resource)
        response = self._resource_obtainer.obtain_resource(resource)
        if not response.ok:
            return [], False
        return [], self.__mp3_validator_proxy.validate_song({
            'source': 'Spider',
            'song': Base64Converter.bytes_to_string(response.content),
            'song_url': resource
        })
        # Or trust the header... I can't find any MPEG 1 Layer 1 or 2 files to test them...
        # return [], True
