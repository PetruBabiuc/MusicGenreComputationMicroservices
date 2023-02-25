from classy_fastapi import Routable
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import config.database


class AbstractDatabaseApiRoutable(Routable):
    def __init__(self):
        super().__init__()

        engine = create_engine(
            f'mariadb+mariadbconnector://{config.database.USER}:{config.database.PASSWORD}'
            f'@{config.database.DB_HOST}:{config.database.DB_PORT}/{config.database.DATABASE}')

        self.__session_maker = sessionmaker(bind=engine)

    def _create_session(self):
        return self.__session_maker()
