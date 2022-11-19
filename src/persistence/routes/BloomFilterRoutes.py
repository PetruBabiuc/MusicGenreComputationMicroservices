from typing import Literal

from classy_fastapi import get, put, delete
from fastapi import Body
from starlette import status
from starlette.responses import Response

import config.database_api as api_paths
from src.model.orm.BloomFilter import BloomFilter
from src.persistence.routes.abstract_classes.AbstractRoutable import AbstractRoutable


class BloomFilterRoutes(AbstractRoutable):
    @get(api_paths.BLOOM_FILTER_PATH)
    def get_bloom_filter(self, user_id: int):
        session = self._create_session()
        bloom_filter = session.get(BloomFilter, user_id)
        if bloom_filter is None:
            return Response(status_code=status.HTTP_404_NOT_FOUND)
        return bloom_filter

    @put(api_paths.BLOOM_FILTER_PATH)
    def put_bloom_filter(self, user_id: int, body: dict[Literal['value'], str] = Body()):
        session = self._create_session()
        bloom_filter = session.get(BloomFilter, user_id)
        if bloom_filter is None:
            bloom_filter = BloomFilter(user_id, body['value'])
            session.add(bloom_filter)
            response = Response(status_code=status.HTTP_201_CREATED)
        else:
            bloom_filter.value = body['value']
            response = Response(status_code=status.HTTP_204_NO_CONTENT)
        session.commit()
        return response

    @delete(api_paths.BLOOM_FILTER_PATH)
    def delete_bloom_filter(self, user_id: int):
        session = self._create_session()
        bloom_filter = session.get(BloomFilter, user_id)
        if bloom_filter is None:
            return Response(status_code=status.HTTP_404_NOT_FOUND)
        session.delete(bloom_filter)
        session.commit()
        return Response(status_code=status.HTTP_200_OK)
