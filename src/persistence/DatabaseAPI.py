from typing import Callable

import uvicorn
from fastapi import FastAPI

from config import database_api
from src.AbstractMicroservice import AbstractMicroservice
from src.persistence.routes.BloomFilterRoutes import BloomFilterRoutes
from src.persistence.routes.CrawlerGeneralStateRoutes import CrawlerGeneralStateRoutes
from src.persistence.routes.IdmRoutes import IdmRoutes
from src.persistence.routes.ResourceUrlRoutes import ResourceUrlRoutes
from src.persistence.routes.ServiceRoutes import ServiceRoutes
from src.persistence.routes.SongGenreRoutes import SongGenreRoutes
from src.persistence.routes.SongRoutes import SongRoutes
from src.persistence.routes.SongUrlRoutes import SongUrlRoutes
from src.persistence.routes.UserRoutes import UserRoutes


class DatabaseAPI(AbstractMicroservice):
    def __init__(self, name: str = 'DatabaseAPI', log_func: Callable[[str], None] = print):
        super().__init__(name, log_func)
        self.__app = FastAPI()
        routes = [UserRoutes, CrawlerGeneralStateRoutes, ResourceUrlRoutes, SongUrlRoutes, ServiceRoutes,
                  SongGenreRoutes, SongRoutes, BloomFilterRoutes, IdmRoutes]
        for route in routes:
            self.__app.include_router(route().router)

    def run(self) -> None:
        uvicorn.run(self.__app, host=database_api.API_HOST, port=database_api.API_PORT)


if __name__ == '__main__':
    DatabaseAPI().run()
