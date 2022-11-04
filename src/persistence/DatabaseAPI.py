from typing import Callable

from flask import Flask
from flask_restful import Api

from config import database_api
from config.database_api import RESOURCES_URLS_PATH, SONG_URLS_PATH, CRAWLER_STATES_PATH, USERS_PATH, SONG_GENRES_PATH, \
    SONGS_PATH, USERS_TO_SERVICES_PATH, SERVICES_PATH
from src.AbstractMicroservice import AbstractMicroservice
from src.persistence.resources.CrawlerStateResource import CrawlerStateResource
from src.persistence.resources.ServicesResource import ServicesResource
from src.persistence.resources.SongGenresResource import SongGenresResource
from src.persistence.resources.SongResource import SongResource
from src.persistence.resources.SongUrlResource import SongUrlResource
from src.persistence.resources.UserResource import UserResource
from src.persistence.resources.ResoureUrlResource import ResourceUrlResource
from src.persistence.resources.UsersToServicesResource import UsersToServicesResource


class DatabaseAPI(AbstractMicroservice):
    def __init__(self, name: str = 'DatabaseAPI', log_func: Callable[[str], None] = print):
        super().__init__(name, log_func)
        self.__app = Flask(__name__)
        self.__api = Api(self.__app)
        self.__api.add_resource(UserResource, USERS_PATH)
        self.__api.add_resource(SongGenresResource, SONG_GENRES_PATH)
        self.__api.add_resource(CrawlerStateResource, f'{CRAWLER_STATES_PATH}/<int:user_id>/')
        self.__api.add_resource(ResourceUrlResource, RESOURCES_URLS_PATH)
        self.__api.add_resource(SongUrlResource, SONG_URLS_PATH)
        self.__api.add_resource(SongResource, SONGS_PATH)
        self.__api.add_resource(UsersToServicesResource, USERS_TO_SERVICES_PATH)
        self.__api.add_resource(ServicesResource, SERVICES_PATH)
        self._log_func(f'[{self._name}] Microservice started on {database_api.API_HOST}:{database_api.API_PORT}!')

    def run(self) -> None:
        self.__app.run(host=database_api.API_HOST, port=database_api.API_PORT)


if __name__ == '__main__':
    DatabaseAPI().run()
