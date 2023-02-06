from classy_fastapi import Routable
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import config.database


class AbstractRoutable(Routable):
    OAUTH2_SCHEME = OAuth2PasswordBearer(tokenUrl="token")

    def __init__(self):
        super().__init__()

        engine = create_engine(
            f'mariadb+mariadbconnector://{config.database.USER}:{config.database.PASSWORD}'
            f'@{config.database.DB_HOST}:{config.database.DB_PORT}/{config.database.DATABASE}')

        self.__session_maker = sessionmaker(bind=engine)

    def _create_session(self):
        return self.__session_maker()
