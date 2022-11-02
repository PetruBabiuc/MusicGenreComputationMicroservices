from flask import jsonify, request

from src.model.orm.OrmUtils import to_dict, query_multidict_to_orm
from src.model.orm.UserToService import UserToService
from src.persistence.resources.abstract_classes.AbstractResource import AbstractResource


class UsersToServicesResource(AbstractResource):
    def get(self):
        session = self._create_session()
        kwargs = query_multidict_to_orm(request.args, UserToService)
        users_to_services = session.query(UserToService).filter_by(**kwargs).all()
        users_to_services = [to_dict(it) for it in users_to_services]
        return jsonify(users_to_services)

    def patch(self):
        session = self._create_session()
        kwargs = query_multidict_to_orm(request.args, UserToService)
        session.query(UserToService).filter_by(**kwargs).update(request.json)
        session.commit()
