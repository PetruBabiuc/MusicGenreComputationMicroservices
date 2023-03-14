from http import HTTPStatus

from classy_fastapi import get
from fastapi import Depends, HTTPException

import config.database_api as api_paths
from config.user_types import USER
from src.model.orm.Bill import Bill
from src.presentation.abstract_classes.routes.AbstractSecuredDatabaseApiRoutable import \
    AbstractSecuredDatabaseApiRoutable


class BillRoutes(AbstractSecuredDatabaseApiRoutable):
    @get(api_paths.USER_BILLS)
    def get_user_bills(self, user_id: int,
                       token: str = Depends(AbstractSecuredDatabaseApiRoutable.OAUTH2_SCHEME)
                       ):
        payload = self._jwt_manager.assert_has_user_type(token, USER)

        if user_id != payload['user_id']:
            raise HTTPException(HTTPStatus.FORBIDDEN)

        session = self._create_session()
        bills = session.query(Bill).filter_by(user_id=user_id).all()
        return bills
