from http import HTTPStatus
from typing import Any

from classy_fastapi import get, put, patch, delete
from fastapi import Body, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.exc import InvalidRequestError, OperationalError, IntegrityError
from starlette.responses import Response

import config.database_api as api_paths
from config.user_types import MICROSERVICE
from src.helpers.ModelUtils import dict_to_orm
from src.model.orm.CrawlerState import CrawlerState
from src.persistence.routes.abstract_classes.AbstractRoutable import AbstractRoutable
from src.persistence.routes.abstract_classes.AbstractSecuredRoutable import AbstractSecuredRoutable


class CrawlerGeneralStateRoutes(AbstractSecuredRoutable):
    @get(api_paths.CRAWLER_GENERAL_STATE_BY_ID_PATH)
    def get_crawler_state(self, user_id: int, token: str = Depends(AbstractRoutable.OAUTH2_SCHEME)):
        self._assert_has_user_type(token, MICROSERVICE)

        session = self._create_session()
        crawler_state = session.get(CrawlerState, user_id)
        if crawler_state is None:
            raise HTTPException(HTTPStatus.NOT_FOUND)
        return crawler_state

    @put(api_paths.CRAWLER_GENERAL_STATE_BY_ID_PATH)
    def put_crawler_state(self, user_id: int, state: dict[str, Any] = Body(),
                          token: str = Depends(AbstractRoutable.OAUTH2_SCHEME)):
        self._assert_has_user_type(token, MICROSERVICE)

        if 'user_id' in state:
            raise HTTPException(HTTPStatus.UNPROCESSABLE_ENTITY)
        try:
            state = dict_to_orm(state, CrawlerState)
        except ValueError:
            raise HTTPException(HTTPStatus.UNPROCESSABLE_ENTITY)
        new_state = CrawlerState(user_id=user_id, **state)
        session = self._create_session()
        old_state = session.get(CrawlerState, user_id)
        if old_state is not None:
            session.delete(old_state)
            session.flush()
            response = Response(status_code=HTTPStatus.NO_CONTENT)
        else:
            response = JSONResponse(state, HTTPStatus.CREATED)
        session.add(new_state)
        session.commit()
        return response

    @patch(api_paths.CRAWLER_GENERAL_STATE_BY_ID_PATH)
    def patch_crawler_state(self, user_id: int, body: dict[str, Any] = Body(),
                            token: str = Depends(AbstractRoutable.OAUTH2_SCHEME)):
        self._assert_has_user_type(token, MICROSERVICE)

        session = self._create_session()
        try:
            session.query(CrawlerState).filter_by(user_id=user_id).update(body)
            session.commit()
            return Response(status_code=HTTPStatus.NO_CONTENT)
        except (InvalidRequestError, OperationalError, IntegrityError):
            raise HTTPException(HTTPStatus.UNPROCESSABLE_ENTITY)

    @delete(api_paths.CRAWLER_GENERAL_STATE_BY_ID_PATH)
    def delete_crawler_state(self, user_id: int, token: str = Depends(AbstractRoutable.OAUTH2_SCHEME)):
        self._assert_has_user_type(token, MICROSERVICE)

        session = self._create_session()
        state = session.get(CrawlerState, user_id)
        if state is None:
            raise HTTPException(HTTPStatus.NOT_FOUND)
        session.delete(state)
        session.commit()
