from fastapi.security import OAuth2PasswordBearer

from src.helpers.security.FastApiJwtManager import FastApiJwtManager
from src.presentation.abstract_classes.routes.AbstractDatabaseApiRoutable import AbstractDatabaseApiRoutable


class AbstractSecuredDatabaseApiRoutable(AbstractDatabaseApiRoutable):
    OAUTH2_SCHEME = OAuth2PasswordBearer(tokenUrl='token')

    def __init__(self):
        super().__init__()
        self._jwt_manager = FastApiJwtManager()
