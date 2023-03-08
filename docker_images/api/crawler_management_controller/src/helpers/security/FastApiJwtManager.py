from http import HTTPStatus

from fastapi import HTTPException
from jose import JWTError

from src.helpers.security.JwtManager import JwtManager


class FastApiJwtManager(JwtManager):
    def __decode_jwt(self, token: str) -> dict:
        try:
            return self.decode_jwt(token)
        except JWTError:
            raise HTTPException(HTTPStatus.FORBIDDEN)

    def assert_has_user_type(self, token: str, user_type: int) -> dict:
        payload = self.__decode_jwt(token)
        if payload['user_type_id'] != user_type:
            raise HTTPException(HTTPStatus.FORBIDDEN)
        return payload

    def assert_has_user_type_in(self, token: str, user_types: list[int]) -> dict:
        payload = self.__decode_jwt(token)
        if payload['user_type_id'] not in user_types:
            raise HTTPException(HTTPStatus.FORBIDDEN)
        return payload
