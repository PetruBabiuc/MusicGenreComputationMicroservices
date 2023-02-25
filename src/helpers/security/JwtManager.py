import re
from datetime import datetime, timedelta
from typing import Any

from jose import jwt, JWTError

from config.jwt import *


class JwtManager:
    def create_jwt(self, claims: dict[str, Any]) -> str:
        claims = claims.copy()
        claims['exp'] = datetime.utcnow() + timedelta(minutes=JWT_MAX_AGE_MINUTES)
        encoded = jwt.encode(claims, SECRET_KEY, algorithm=ALGORITHM)
        return encoded

    def decode_jwt(self, encoded_jwt: str) -> dict[str, Any]:
        if encoded_jwt.count('.') != 2:
            raise JWTError('Invalid JWT format!')
        return jwt.decode(encoded_jwt, SECRET_KEY, algorithms=ALGORITHM)
