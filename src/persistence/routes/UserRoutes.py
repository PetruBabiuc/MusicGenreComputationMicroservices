from http import HTTPStatus

from classy_fastapi import get, post
from fastapi import Depends, HTTPException

import config.database_api as api_paths
from config.user_types import ADMIN
from src.helpers.ModelUtils import orm_to_dict
from src.model.orm.User import User
from src.presentation.abstract_classes.routes.AbstractSecuredDatabaseApiRoutable import \
    AbstractSecuredDatabaseApiRoutable


class UserRoutes(AbstractSecuredDatabaseApiRoutable):
    @get(api_paths.USERS_PATH)
    def get_users(self, token: str = Depends(AbstractSecuredDatabaseApiRoutable.OAUTH2_SCHEME)):
        self._jwt_manager.assert_has_user_type(token, ADMIN)

        session = self._create_session()
        users = session.query(User).all()

        users = [orm_to_dict(user) for user in users]
        for user in users:
            del user['password']

        return users

    @post(api_paths.TOGGLE_USER_ACTIVE_PATH)
    def toggle_user_active(self, user_id: int, token: str = Depends(AbstractSecuredDatabaseApiRoutable.OAUTH2_SCHEME)):
        self._jwt_manager.assert_has_user_type(token, ADMIN)

        session = self._create_session()
        user: User = session.get(User, user_id)
        if user is None:
            return HTTPException(HTTPStatus.NOT_FOUND)

        user.is_active = not user.is_active
        session.commit()
