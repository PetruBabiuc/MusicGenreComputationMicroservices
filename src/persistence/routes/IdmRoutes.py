from typing import Literal, Union

from classy_fastapi import post
from fastapi import Body, HTTPException, Depends
from jose import JWTError
from sqlalchemy.exc import IntegrityError
from starlette.responses import Response
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_422_UNPROCESSABLE_ENTITY, HTTP_201_CREATED, HTTP_409_CONFLICT, \
    HTTP_403_FORBIDDEN

import config.database_api as api_paths
from config import user_types
from src.helpers.abstract_classes.JwtBlacklistInterface import JwtBlacklistInterface
from src.helpers.security.BlacklistFastApiJwtManager import BlacklistFastApiJwtManager
from src.helpers.security.PasswordManager import PasswordManager
from src.model.orm.Service import Service
from src.model.orm.User import User
from src.model.orm.UserToService import UserToService
from src.presentation.abstract_classes.routes.AbstractSecuredDatabaseApiRoutable import \
    AbstractSecuredDatabaseApiRoutable


class IdmRoutes(AbstractSecuredDatabaseApiRoutable):
    __USER_NAME_FIELD = 'user_name'
    __PASSWORD_FIELD = 'password'

    def __init__(self, jwt_manager: BlacklistFastApiJwtManager):
        super().__init__(jwt_manager)
        self.__password_manager = PasswordManager()
        self.__jwt_blacklist: JwtBlacklistInterface = jwt_manager

    @post(api_paths.LOGIN_PATH)
    def login(self, body: dict[str, str] = Body()):
        if self.__USER_NAME_FIELD not in body or self.__PASSWORD_FIELD not in body:
            raise HTTPException(HTTP_422_UNPROCESSABLE_ENTITY,
                                f'Required fields: {self.__USER_NAME_FIELD}, {self.__PASSWORD_FIELD}')
        user_name = body[self.__USER_NAME_FIELD]
        password = body[self.__PASSWORD_FIELD]

        session = self._create_session()
        user: User = session.query(User).filter_by(user_name=user_name).first()

        if user is None:
            raise HTTPException(HTTP_401_UNAUTHORIZED, 'Invalid credentials!')

        if not self.__password_manager.verify_password(password, user.password):
            raise HTTPException(HTTP_401_UNAUTHORIZED, 'Invalid credentials!')

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
    def validate_jwt(self, body: dict[Literal['jwt'], str],
                     token: str = Depends(AbstractSecuredDatabaseApiRoutable.OAUTH2_SCHEME)):
        self._jwt_manager.assert_has_user_type(token, user_types.MICROSERVICE)
        try:
            payload = self._jwt_manager.decode_jwt(body['jwt'])
            pass
        except Union[JWTError, HTTPException] as e:
            return {'status': 'invalid'}
        return {'status': 'valid'}

    @post(api_paths.LOGOUT_PATH)
    def logout(self, token: str = Depends(AbstractSecuredDatabaseApiRoutable.OAUTH2_SCHEME)):
        try:
            payload = self._jwt_manager.decode_jwt(token)
        except JWTError:
            raise HTTPException(HTTP_403_FORBIDDEN)

        self.__jwt_blacklist.blacklist_jwt(token, payload['exp'])

    @post(api_paths.REGISTER_PATH)
    def register(self, body: dict[str, str] = Body()):
        if self.__USER_NAME_FIELD not in body or self.__PASSWORD_FIELD not in body:
            raise HTTPException(HTTP_422_UNPROCESSABLE_ENTITY,
                                f'Required fields: {self.__USER_NAME_FIELD}, {self.__PASSWORD_FIELD}')

        user_name = body[self.__USER_NAME_FIELD]
        password = body[self.__PASSWORD_FIELD]

        for field in user_name, password:
            if not 5 <= len(field) <= 30:
                raise HTTPException(HTTP_422_UNPROCESSABLE_ENTITY,
                                    'The fields should have the length between 5 and 30 characters!')

        password = self.__password_manager.hash_password(password)
        session = self._create_session()
        user = User(user_name=user_name, password=password, is_active=True, user_type_id=user_types.USER)
        try:
            session.add(user)
            services = session.query(Service).all()
            user_services = [UserToService(user.user_id, s.service_id, 0) for s in services]
            session.add_all(user_services)
            session.commit()
        except IntegrityError as ex:
            raise HTTPException(HTTP_409_CONFLICT, 'Username already taken')
        return Response(status_code=HTTP_201_CREATED)
