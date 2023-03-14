from typing import Callable

from config import database_api
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


class DatabaseAPI(AbstractFastApiController):
    def __init__(self, name: str = 'DatabaseAPI', log_func: Callable[[str], None] = print):
        routes = [UserRoutes(), CrawlerGeneralStateRoutes(), ResourceUrlRoutes(), SongUrlRoutes(), ServiceRoutes(),
                  SongGenreRoutes(), SongRoutes(), BloomFilterRoutes(), IdmRoutes(), BillRoutes()]

        super().__init__(routes, name, database_api.API_HOST, database_api.API_PORT, log_func)


if __name__ == '__main__':
    DatabaseAPI().run()
