from typing import Literal

from classy_fastapi import post
from fastapi import Body, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

import config.database_api as api_paths
from config import user_types
from src.helpers.security.PasswordManager import PasswordManager
from src.model.orm.User import User
from src.persistence.routes.abstract_classes.AbstractRoutable import AbstractRoutable
from src.persistence.routes.abstract_classes.AbstractSecuredRoutable import AbstractSecuredRoutable


class IdmRoutes(AbstractSecuredRoutable):
    __USER_NAME_FIELD = 'user_name'
    __PASSWORD_FIELD = 'password'

    def __init__(self):
        super().__init__()
        self.__oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
        self.__password_manager = PasswordManager()

    @post(api_paths.LOGIN_PATH)
    def login(self, body: dict[str, str] = Body()):
        if self.__USER_NAME_FIELD not in body or self.__PASSWORD_FIELD not in body:
            raise HTTPException(422, f'Required fields: {self.__USER_NAME_FIELD}, {self.__PASSWORD_FIELD}')

        user_name = body[self.__USER_NAME_FIELD]
        password = body[self.__PASSWORD_FIELD]

        session = self._create_session()
        user: User = session.query(User).filter_by(user_name=user_name).one()

        if not self.__password_manager.verify_password(password, user.password):
            raise HTTPException(401, 'Invalid credentials!')

        claims = {
            'iss': api_paths.API_URL_PREFIX,
            'sub': user.user_name,
            'user_id': user.user_id,
            'is_active': user.is_active,
            'user_type_id': user.user_type_id
        }
        jwt = self._jwt_manager.create_jwt(claims)
        return {'jwt': jwt}

    @post(api_paths.VALIDATE_JWT_PATH)
    def validate_jwt(self, body: dict[Literal['jwt'], str], token: str = Depends(AbstractRoutable.OAUTH2_SCHEME)):
        self._assert_has_user_type(token, user_types.MICROSERVICE)
        try:
            payload = self._jwt_manager.decode_jwt(body['jwt'])
            pass
        except JWTError as e:
            return {'status': 'invalid'}
        return {'status': 'valid'}

    @post(api_paths.LOGOUT_PATH)
    def logout(self, token: str = Depends(AbstractRoutable.OAUTH2_SCHEME)):
        # TODO: Use a JWT Blacklist/other means to invalidate JWT
        return
