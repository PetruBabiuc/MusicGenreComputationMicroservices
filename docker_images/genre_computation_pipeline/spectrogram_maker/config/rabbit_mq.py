import os
from dataclasses import dataclass


@dataclass
class RabbitMqQueueInfo:
    exchange: str
    routing_key: str
    name: str


HOST = os.getenv('rabbit_mq_host', '0.0.0.0')
PORT = 5678
USERNAME = 'student'
PASSWORD = 'student'
PREFIX = 'licenta'
EXCHANGE = f'{PREFIX}.direct'


class GenreComputationPipeline:
    SONGS_QUEUE = RabbitMqQueueInfo(EXCHANGE, f'{PREFIX}.songsQueue.routingKey', f'{PREFIX}.songsQueue')
    SLICES_QUEUE = RabbitMqQueueInfo(EXCHANGE, f'{PREFIX}.slicesQueue.routingKey', f'{PREFIX}.slicesQueue')
    SLICES_DATA_QUEUE = RabbitMqQueueInfo(EXCHANGE, f'{PREFIX}.slicesDataQueue.routingKey', f'{PREFIX}.slicesDataQueue')


class Crawler:
    class Spiders:
        RESTORE_STATE_QUEUE = RabbitMqQueueInfo(EXCHANGE, f'{PREFIX}.spiderRestoreStateQueue.routingKey',
                                                f'{PREFIX}.spiderRestoreStateQueue')
        RETURN_QUEUE = RabbitMqQueueInfo(EXCHANGE, f'{PREFIX}.spiderReturnQueue.routingKey',
                                         f'{PREFIX}.spiderReturnQueue')

    class UrlProcessors:
        RESTORE_STATE_QUEUE = RabbitMqQueueInfo(EXCHANGE, f'{PREFIX}.songUrlProcessorRestoreState.routingKey',
                                                f'{PREFIX}.songUrlProcessorRestoreState')
        RETURN_QUEUE = RabbitMqQueueInfo(EXCHANGE, f'{PREFIX}.songUrlProcessorReturnQueue.routingKey',
                                         f'{PREFIX}.songUrlProcessorReturnQueue')


MP3_VERIFIER_QUEUE = RabbitMqQueueInfo(EXCHANGE, f'{PREFIX}.mp3VerifierQueue.routingKey', f'{PREFIX}.mp3VerifierQueue')
