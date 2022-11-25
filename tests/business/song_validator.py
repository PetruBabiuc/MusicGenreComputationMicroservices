import time
import unittest
from multiprocessing import Process

from config.redis import SPIDER_TOPIC, CONTROLLER_TOPIC
from main import instantiate_and_run
from src.business.Mp3Validator import Mp3Validator
from src.helpers import Base64Converter
from src.helpers.Mp3ValidatorProxy import Mp3ValidatorProxy
from tests.presentation.tests import test4, request_song_genre_v2


class Mp3ValidatorLocalTests(unittest.TestCase):
    mp3_validator_process: Process = None
    controller_proxy: Mp3ValidatorProxy
    spider_proxy: Mp3ValidatorProxy

    @classmethod
    def setUpClass(cls):
        cls.mp3_validator_process = Process(target=instantiate_and_run, args=(Mp3Validator, ()))
        cls.mp3_validator_process.start()
        time.sleep(2)
        cls.controller_proxy = Mp3ValidatorProxy(CONTROLLER_TOPIC, 'song_id')
        cls.spider_proxy = Mp3ValidatorProxy(SPIDER_TOPIC, 'song_url')

    @classmethod
    def controller_check_function(cls, song: bytes) -> bool:
        return cls.controller_proxy.validate_song({
            'song_id': 33,
            'song': Base64Converter.bytes_to_string(song),
            'source': 'Controller'
        })

    @classmethod
    def spider_check_function(cls, song: bytes) -> bool:
        return cls.spider_proxy.validate_song({
            'song_url': 'wasd1234',
            'song': Base64Converter.bytes_to_string(song),
            'source': 'Spider'
        })

    def test_ok_controller(self):
        with open('../../debug_files/Controller - Song.mp3', 'rb') as f:
            song = f.read()
        self.assertTrue(self.controller_check_function(song))

    def test_ok_spider(self):
        with open('../../debug_files/Controller - Song.mp3', 'rb') as f:
            song = f.read()
        self.assertTrue(self.spider_check_function(song))

    @classmethod
    def tearDown(cls) -> None:
        cls.mp3_validator_process.terminate()

class Mp3ValidatorIntegrationTests(unittest.TestCase):
    def test_controller_ok(self):
        song_path = '../../../DeepAudioClassification-master/Data/Raw/petru/[YT2mp3.info] - Lil Jon & The East Side Boyz - Get Low (feat. Ying Yang Twins) (Official Music Video) (320kbps).mp3'
        request_song_genre_v2(1, song_path)

    def test_controller_not_mp3(self):
        invalid_song_path = '../../main.py'
        request_song_genre_v2(1, invalid_song_path)

    def test_controller_mp3_too_short(self):
        song_path = '../auxiliary_files/658370_13579627-lq.mp3'
        request_song_genre_v2(1, song_path)
