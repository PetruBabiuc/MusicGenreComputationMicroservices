from http import HTTPStatus
from typing import Literal

from classy_fastapi import get, put, delete
from fastapi import Body, Depends, HTTPException
from starlette.responses import Response

import config.database_api as api_paths
from config.user_types import MICROSERVICE
from src.model.orm.BloomFilter import BloomFilter
from src.presentation.abstract_classes.routes.AbstractSecuredDatabaseApiRoutable import AbstractSecuredDatabaseApiRoutable


class BloomFilterRoutes(AbstractSecuredDatabaseApiRoutable):
    @get(api_paths.BLOOM_FILTER_PATH)
    def get_bloom_filter(self, user_id: int,
                         token: str = Depends(AbstractSecuredDatabaseApiRoutable.OAUTH2_SCHEME)):
        self._jwt_manager.assert_has_user_type(token, MICROSERVICE)

        session = self._create_session()
        bloom_filter = session.get(BloomFilter, user_id)
        if bloom_filter is None:
            raise HTTPException(HTTPStatus.NOT_FOUND)
        return bloom_filter

    @put(api_paths.BLOOM_FILTER_PATH)
    def put_bloom_filter(self, user_id: int, body: dict[Literal['value'], str] = Body(),
                         token: str = Depends(AbstractSecuredDatabaseApiRoutable.OAUTH2_SCHEME)):
        self._jwt_manager.assert_has_user_type(token, MICROSERVICE)

        session = self._create_session()
        bloom_filter = session.get(BloomFilter, user_id)
        if bloom_filter is None:
            bloom_filter = BloomFilter(user_id, body['value'])
            session.add(bloom_filter)
            response = Response(status_code=HTTPStatus.CREATED)
        else:
            bloom_filter.value = body['value']
            response = Response(status_code=HTTPStatus.NO_CONTENT)
        session.commit()
        return response

    @delete(api_paths.BLOOM_FILTER_PATH)
    def delete_bloom_filter(self, user_id: int, token: str = Depends(AbstractSecuredDatabaseApiRoutable.OAUTH2_SCHEME)):
        self._jwt_manager.assert_has_user_type(token, MICROSERVICE)

        session = self._create_session()
        bloom_filter = session.get(BloomFilter, user_id)
        if bloom_filter is None:
            raise HTTPException(HTTPStatus.NOT_FOUND)
        session.delete(bloom_filter)
        session.commit()
