from classy_fastapi import Routable
from fastapi.security import OAuth2PasswordBearer

from src.helpers.security.FastApiJwtManager import FastApiJwtManager


class AbstractSecuredRoutable(Routable):
    OAUTH2_SCHEME = OAuth2PasswordBearer(tokenUrl='token')

    def __init__(self) -> None:
        super().__init__()
        self._jwt_manager = FastApiJwtManager()
