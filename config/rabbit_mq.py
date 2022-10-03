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

SONGS_QUEUE = RabbitMqQueueInfo(EXCHANGE, 'licenta.songsQueue.routingKey', 'licenta.songsQueue')
SLICES_QUEUE = RabbitMqQueueInfo(EXCHANGE, 'licenta.slicesQueue.routingKey', 'licenta.slicesQueue')
SLICES_DATA_QUEUE = RabbitMqQueueInfo(EXCHANGE, 'licenta.slicesDataQueue.routingKey', 'licenta.slicesDataQueue')
