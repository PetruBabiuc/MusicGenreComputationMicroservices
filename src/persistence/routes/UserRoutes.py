from classy_fastapi import get
from fastapi import Depends

import config.database_api as api_paths
from config.user_types import ADMIN
from src.model.orm.User import User
from src.persistence.routes.abstract_classes.AbstractRoutable import AbstractRoutable
from src.persistence.routes.abstract_classes.AbstractSecuredRoutable import AbstractSecuredRoutable


class UserRoutes(AbstractSecuredRoutable):
    @get(api_paths.USERS_PATH)
    def get_users(self, token: str = Depends(AbstractRoutable.OAUTH2_SCHEME)):
        self._assert_has_user_type(token, ADMIN)

        session = self._create_session()
        users = session.query(User).all()
        return users
