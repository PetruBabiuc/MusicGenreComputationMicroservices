from typing import Any

from classy_fastapi import get, put, patch, delete
from fastapi import status, Body
from fastapi.responses import JSONResponse
from sqlalchemy.exc import InvalidRequestError, OperationalError, IntegrityError
from starlette.responses import Response

import config.database_api as api_paths
from src.helpers.ModelUtils import dict_to_orm
from src.model.orm.CrawlerState import CrawlerState
from src.persistence.routes.abstract_classes.AbstractRoutable import AbstractRoutable


class CrawlerGeneralStateRoutes(AbstractRoutable):
    @get(api_paths.CRAWLER_GENERAL_STATE_BY_ID_PATH)
    def get_crawler_state(self, user_id: int):
        session = self._create_session()
        crawler_state = session.get(CrawlerState, user_id)
        if crawler_state is None:
            return Response(status_code=status.HTTP_404_NOT_FOUND)
        return crawler_state

    @put(api_paths.CRAWLER_GENERAL_STATE_BY_ID_PATH)
    def put_crawler_state(self, user_id: int, state: dict[str, Any] = Body()):
        if 'user_id' in state:
            return Response(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
        try:
            state = dict_to_orm(state, CrawlerState)
        except ValueError:
            return Response(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
        new_state = CrawlerState(user_id=user_id, **state)
        session = self._create_session()
        old_state = session.get(CrawlerState, user_id)
        if old_state is not None:
            session.delete(old_state)
            session.flush()
            response = Response(status_code=status.HTTP_204_NO_CONTENT)
        else:
            response = JSONResponse(state, status.HTTP_201_CREATED)
        session.add(new_state)
        session.commit()
        return response

    @patch(api_paths.CRAWLER_GENERAL_STATE_BY_ID_PATH)
    def patch_crawler_state(self, user_id: int, body: dict[str, Any] = Body()):
        session = self._create_session()
        try:
            session.query(CrawlerState).filter_by(user_id=user_id).update(body)
            session.commit()
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        except (InvalidRequestError, OperationalError, IntegrityError):
            return Response(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

    @delete(api_paths.CRAWLER_GENERAL_STATE_BY_ID_PATH)
    def delete_crawler_state(self, user_id: int):
        session = self._create_session()
        state = session.get(CrawlerState, user_id)
        if state is None:
            return Response(status_code=status.HTTP_404_NOT_FOUND)
        session.delete(state)
        session.commit()
        return Response(status_code=status.HTTP_200_OK)
