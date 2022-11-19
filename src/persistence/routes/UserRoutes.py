from classy_fastapi import get

import config.database_api as api_paths
from src.model.orm.User import User
from src.persistence.routes.abstract_classes.AbstractRoutable import AbstractRoutable


class UserRoutes(AbstractRoutable):
    @get(api_paths.USERS_PATH)
    def get_users(self):
        session = self._create_session()
        users = session.query(User).all()
        return users
