import os

HOST = os.getenv('redis_host', '0.0.0.0')
PORT = 6379

CONTROLLER_TOPIC = 'controller_topic'
SPIDER_TOPIC = 'spider_topic'
