from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from typing import Callable

from config import crawler_engine
from config.crawler_management_controller import HOST, CLIENT_PORT, CRAWLER_RESPONSES_PORT
from src.helpers.HighLevelSocketWrapper import HighLevelSocketWrapper
from src.helpers.SocketJsonMessageAwaiter import SocketJsonMessageAwaiter
from src.presentation.abstract_classes.AbstractFastApiController import AbstractFastApiController
from src.presentation.crawler_management.routes.CrawlerRoutes import CrawlerRoutes


class CrawlerManagementController(AbstractFastApiController):
    def __init__(self, name: str = 'CrawlerManagementController', log_func: Callable[[str], None] = print):
        self.__crawling_results_awaiter: SocketJsonMessageAwaiter[int] = SocketJsonMessageAwaiter(
            HOST, CRAWLER_RESPONSES_PORT, 'client_id'
        )

        super().__init__([CrawlerRoutes(self.__crawl, name, log_func)], name, HOST, CLIENT_PORT, log_func)

    def __crawl(self, user_id: int) -> dict:
        # Putting awaitable response
        self.__crawling_results_awaiter.put_awaitable(user_id)

        # Forwarding the request to the crawler
        crawler_socket = HighLevelSocketWrapper(socket(AF_INET, SOCK_STREAM))
        crawler_socket.connect((crawler_engine.HOST, crawler_engine.PORT))
        crawler_socket.send_dict_as_json({'client_id': user_id})
        crawler_socket.close()

        # Waiting for the response
        result = self.__crawling_results_awaiter.await_result(user_id)
        return result

    def run(self) -> None:
        Thread(target=self.__crawling_results_awaiter.start_receiving_responses).start()
        super().run()
