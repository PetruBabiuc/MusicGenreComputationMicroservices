from classy_fastapi import get
from fastapi import Depends

import config.database_api as api_paths
from config.user_types import ADMIN
from src.model.orm.User import User
from src.presentation.abstract_classes.routes.AbstractSecuredDatabaseApiRoutable import AbstractSecuredDatabaseApiRoutable


class UserRoutes(AbstractSecuredDatabaseApiRoutable):
    @get(api_paths.USERS_PATH)
    def get_users(self, token: str = Depends(AbstractSecuredDatabaseApiRoutable.OAUTH2_SCHEME)):
        self._jwt_manager.assert_has_user_type(token, ADMIN)

        session = self._create_session()
        users = session.query(User).all()
        return users
