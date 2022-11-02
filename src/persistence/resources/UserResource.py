from flask import jsonify

from src.model.orm.OrmUtils import to_dict
from src.model.orm.User import User
from src.persistence.resources.abstract_classes.AbstractResource import AbstractResource


class UserResource(AbstractResource):
    def get(self):
        session = self._create_session()
        users = session.query(User).all()
        users = [to_dict(it) for it in users]
        return jsonify(users)
