from flask_restful import Resource
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import database


class AbstractResource(Resource):
    def __init__(self):
        engine = create_engine(
            f'mariadb+mariadbconnector://{database.USER}:{database.PASSWORD}'
            f'@{database.DB_HOST}:{database.DB_PORT}/{database.DATABASE}')
        self.__session_maker = sessionmaker(bind=engine)

    def _create_session(self):
        return self.__session_maker()
