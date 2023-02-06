from http import HTTPStatus

from fastapi import HTTPException
from jose import JWTError

from src.helpers.security.JwtManager import JwtManager
from src.persistence.routes.abstract_classes.AbstractRoutable import AbstractRoutable


class AbstractSecuredRoutable(AbstractRoutable):
    FORBIDDEN_DETAILS = 'Forbidden'

    def __init__(self):
        super().__init__()
        self._jwt_manager = JwtManager()

    def __decode_jwt(self, token: str) -> dict:
        try:
            return self._jwt_manager.decode_jwt(token)
        except JWTError:
            raise HTTPException(HTTPStatus.FORBIDDEN, self.FORBIDDEN_DETAILS)

    def _assert_has_user_type(self, token: str, user_type: int) -> dict:
        payload = self.__decode_jwt(token)
        if payload['user_type_id'] != user_type:
            raise HTTPException(HTTPStatus.FORBIDDEN, self.FORBIDDEN_DETAILS)
        return payload

    def _assert_has_user_type_in(self, token: str, user_types: list[int]) -> dict:
        payload = self.__decode_jwt(token)
        if payload['user_type_id'] not in user_types:
            raise HTTPException(HTTPStatus.FORBIDDEN, self.FORBIDDEN_DETAILS)
        return payload
