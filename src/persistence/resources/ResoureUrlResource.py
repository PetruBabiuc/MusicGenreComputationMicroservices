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
        if request.args.get('bulk', default=False):
            user_id = int(request.args['user_id'])
            resources_urls = [ResourceUrl(user_id=user_id, resource_url=url) for url in request.json]
            session.add_all(resources_urls)
        else:
            data = request.json
            resource_url = ResourceUrl(**data)
            session.add(resource_url)
        session.commit()

    def delete(self):
        session = self._create_session()
        if request.args.get('bulk', False):
            resources_urls_ids = request.json
            session.query(ResourceUrl).filter(ResourceUrl.resource_url_id.in_(resources_urls_ids)).delete()
        else:
            kwargs = query_multidict_to_orm(request.args, ResourceUrl)
            session.query(ResourceUrl).filter_by(**kwargs).delete()
        session.commit()
