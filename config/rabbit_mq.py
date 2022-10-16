from dataclasses import dataclass


@dataclass
class RabbitMqQueueInfo:
    exchange: str
    routing_key: str
    name: str


HOST = '0.0.0.0'
PORT = 5678
USERNAME = 'student'
PASSWORD = 'student'
EXCHANGE = 'licenta.direct'


class GenreComputationPipeline:
    SONGS_QUEUE = RabbitMqQueueInfo(EXCHANGE, 'licenta.songsQueue.routingKey', 'licenta.songsQueue')
    SLICES_QUEUE = RabbitMqQueueInfo(EXCHANGE, 'licenta.slicesQueue.routingKey', 'licenta.slicesQueue')
    SLICES_DATA_QUEUE = RabbitMqQueueInfo(EXCHANGE, 'licenta.slicesDataQueue.routingKey', 'licenta.slicesDataQueue')


class Crawler:
    class Spiders:
        RESTORE_STATE_QUEUE = RabbitMqQueueInfo(EXCHANGE, 'licenta.spiderRestoreStateQueue.routingKey',
                                                'licenta.spiderRestoreStateQueue')
        RETURN_QUEUE = RabbitMqQueueInfo(EXCHANGE, 'licenta.spiderReturnQueue.routingKey',
                                         'licenta.spiderReturnQueue')

    class UrlProcessors:
        RESTORE_STATE_QUEUE = RabbitMqQueueInfo(EXCHANGE, 'licenta.songUrlProcessorRestoreState.routingKey',
                                                'licenta.songUrlProcessorRestoreState')
        RETURN_QUEUE = RabbitMqQueueInfo(EXCHANGE, 'licenta.songUrlProcessorReturnQueue.routingKey',
                                         'licenta.songUrlProcessorReturnQueue')
