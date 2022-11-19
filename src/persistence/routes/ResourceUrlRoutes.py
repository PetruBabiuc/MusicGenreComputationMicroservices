from typing import Any

from classy_fastapi import get, post
from fastapi import Body
from starlette import status
from starlette.responses import Response, JSONResponse

import config.database_api as api_paths
from src.helpers.ModelUtils import orm_to_dict
from src.model.orm.ResourceUrl import ResourceUrl
from src.persistence.routes.abstract_classes.AbstractRoutable import AbstractRoutable


class ResourceUrlRoutes(AbstractRoutable):
    @get(api_paths.CRAWLER_RESOURCES_URLS_PATH)
    def get_resources_urls(self, user_id: int, limit: int = None):
        session = self._create_session()
        query = session.query(ResourceUrl).filter_by(user_id=user_id)
        if limit is not None and limit > 0:
            query = query.limit(limit)
        urls = query.all()
        urls = [orm_to_dict(url) for url in urls]
        for url in urls:
            del url['user_id']
        return urls

    @get(api_paths.CRAWLER_RESOURCES_URLS_COUNT_PATH)
    def get_resources_urls_count(self, user_id: int):
        session = self._create_session()
        count = session.query(ResourceUrl).filter_by(user_id=user_id).count()
        return {'count': count}

    @post(api_paths.CRAWLER_RESOURCES_URLS_PATH)
    def post_url_resource(self, user_id: int, body: dict[str, Any] = Body()):
        session = self._create_session()
        resource_url = ResourceUrl(user_id=user_id, **body)
        session.add(resource_url)
        session.commit()
        return resource_url

    @post(api_paths.CRAWLER_RESOURCES_URLS_BULK_DELETE_PATH)
    def bulk_delete_resources_urls(self, user_id: int, resources_urls_ids: list[int] = Body()):
        session = self._create_session()
        session.query(ResourceUrl)\
            .filter_by(user_id=user_id)\
            .filter(ResourceUrl.resource_url_id.in_(resources_urls_ids))\
            .delete()
        session.commit()
        return Response(status_code=status.HTTP_200_OK)

    @post(api_paths.CRAWLER_RESOURCES_URLS_BULK_ADD_PATH)
    def bulk_post_resources_urls(self, user_id: int, resources_urls: list[str] = Body()):
        session = self._create_session()
        resources_urls = [ResourceUrl(user_id=user_id, resource_url=url) for url in resources_urls]
        session.add_all(resources_urls)
        session.commit()
        return JSONResponse([res.resource_url_id for res in resources_urls], status_code=status.HTTP_200_OK)
