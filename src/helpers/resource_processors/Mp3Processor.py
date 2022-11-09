from __future__ import annotations

from io import BytesIO
from urllib.parse import urljoin

from mutagen.mp3 import MP3

from config.constants import CRAWLED_SONG_MIN_LENGTH, CRAWLED_SONG_MAX_LENGTH
from src.helpers.abstract_classes.AbstractMimeContentProcessor import AbstractMimeContentProcessor
from src.helpers.resource_obtainers.SimpleResourceObtainer import SimpleResourceObtainer


class Mp3Processor(AbstractMimeContentProcessor):
    def __init__(self):
        types = ['audio/mpeg']
        obtainer = SimpleResourceObtainer()
        super().__init__(types, obtainer)

    def process_resource(self, resource: str, domain: str) -> tuple[list[str], bool]:
        # TODO: REMOVE
        # return [], True
        # Test if the response's content is an MP3
        resource = urljoin(domain, resource)
        response = self._resource_obtainer.obtain_resource(resource)
        if not response.ok:
            return [], False
        try:
            song = response.content
            song = BytesIO(song)
            song = MP3(song)
            return [], CRAWLED_SONG_MIN_LENGTH <= song.info.length <= CRAWLED_SONG_MAX_LENGTH
        except BaseException:
            return [], False

        # Or trust the header... I can't find any MPEG 1 Layer 1 or 2 files to test them...
        # return [], True
