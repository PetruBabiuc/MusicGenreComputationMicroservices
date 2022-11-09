from flask_restful import Resource
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import config.database


class AbstractResource(Resource):
    def __init__(self):
        engine = create_engine(
            f'mariadb+mariadbconnector://{config.database.USER}:{config.database.PASSWORD}'
            f'@{config.database.DB_HOST}:{config.database.DB_PORT}/{config.database.DATABASE}')
        self.__session_maker = sessionmaker(bind=engine)

    def _create_session(self):
        return self.__session_maker()
