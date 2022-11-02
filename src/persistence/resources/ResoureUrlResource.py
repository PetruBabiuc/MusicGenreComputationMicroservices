from flask import jsonify, request

from src.model.orm.OrmUtils import query_multidict_to_orm, to_dict
from src.model.orm.ResourceUrl import ResourceUrl
from src.persistence.resources.abstract_classes.AbstractResource import AbstractResource


class ResourceUrlResource(AbstractResource):
    def get(self):
        session = self._create_session()
        kwargs = query_multidict_to_orm(request.args, ResourceUrl)
        resource_urls = session.query(ResourceUrl).filter_by(**kwargs).all()
        resource_urls = [to_dict(resource_url) for resource_url in resource_urls]
        return jsonify(resource_urls)

    def post(self):
        session = self._create_session()
        data = request.json
        resource_url = ResourceUrl(**data)
        session.add(resource_url)
        session.commit()

    def delete(self):
        kwargs = query_multidict_to_orm(request.args, ResourceUrl)
        session = self._create_session()
        session.query(ResourceUrl).filter_by(**kwargs).delete()
        session.commit()
