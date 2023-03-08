import json
import time
from typing import Callable

from config.rabbit_mq import Crawler
from src.business.abstract_classes.AbstractMp3SpiderMicroservice import AbstractMp3SpiderMicroservice
from src.helpers.RabbitMqConsumer import RabbitMqConsumer
from src.helpers.RabbitMqProducer import RabbitMqProducer
from src.model.SpiderReturn import SpiderReturn


class Mp3SpiderMicroservice(AbstractMp3SpiderMicroservice):
    def __init__(self, name: str = 'Mp3Spider', log_func: Callable[[str], None] = print):
        super().__init__(name, log_func)
        self.__receiver = RabbitMqConsumer(Crawler.Spiders.RESTORE_STATE_QUEUE.name, self._on_received_message)
        self.__sender = RabbitMqProducer(Crawler.Spiders.RETURN_QUEUE.exchange,
                                         Crawler.Spiders.RETURN_QUEUE.routing_key)
        self._log_func(f'[{self._name}] Microservice started!')

    def _schedule_domain_request(self, domain: str):
        time.sleep(0.25)  # TODO

    def _send_spider_return(self, client_id, spider_return: SpiderReturn) -> None:
        message = spider_return.__dict__
        message['client_id'] = client_id
        message = json.dumps(message).encode()
        self.__sender.send_message(message)

    def run(self) -> None:
        self.__receiver.start_receiving_messages()


if __name__ == '__main__':
    Mp3SpiderMicroservice().run()
