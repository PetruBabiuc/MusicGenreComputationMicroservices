from threading import Thread
from typing import Callable, Type

from classy_fastapi import Routable

from config import database_api
from src.helpers.security.BlacklistFastApiJwtManager import BlacklistFastApiJwtManager
from src.persistence.routes.BillRoutes import BillRoutes
from src.persistence.routes.BloomFilterRoutes import BloomFilterRoutes
from src.persistence.routes.CrawlerGeneralStateRoutes import CrawlerGeneralStateRoutes
from src.persistence.routes.IdmRoutes import IdmRoutes
from src.persistence.routes.ResourceUrlRoutes import ResourceUrlRoutes
from src.persistence.routes.ServiceRoutes import ServiceRoutes
from src.persistence.routes.SongGenreRoutes import SongGenreRoutes
from src.persistence.routes.SongRoutes import SongRoutes
from src.persistence.routes.SongUrlRoutes import SongUrlRoutes
from src.persistence.routes.UserRoutes import UserRoutes
from src.presentation.abstract_classes.AbstractFastApiController import AbstractFastApiController
from src.presentation.abstract_classes.routes.AbstractDatabaseApiRoutable import AbstractDatabaseApiRoutable
from src.presentation.abstract_classes.routes.AbstractSecuredDatabaseApiRoutable import \
    AbstractSecuredDatabaseApiRoutable


class DatabaseAPI(AbstractFastApiController):
    def __init__(self, name: str = 'DatabaseAPI', log_func: Callable[[str], None] = print):
        self.__jwt_manager = BlacklistFastApiJwtManager()
        secured_routable_classes: list[Type[AbstractSecuredDatabaseApiRoutable]] = [
            UserRoutes, CrawlerGeneralStateRoutes, ResourceUrlRoutes, SongUrlRoutes, ServiceRoutes, SongRoutes,
            BloomFilterRoutes, IdmRoutes, BillRoutes
        ]

        routable_classes: list[Type[AbstractDatabaseApiRoutable]] = [SongGenreRoutes]

        routes: list[AbstractDatabaseApiRoutable] = [it(self.__jwt_manager) for it in secured_routable_classes] + \
                                                    [it() for it in routable_classes]

        super().__init__(routes, name, database_api.API_HOST, database_api.API_PORT, log_func)

    def run(self) -> None:
        Thread(target=self.__jwt_manager.start_blacklist_cleaning).start()
        super().run()


if __name__ == '__main__':
    DatabaseAPI().run()
