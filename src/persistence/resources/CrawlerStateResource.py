from flask import jsonify, request

from src.model.orm.SongGenre import SongGenre
from src.model.orm.CrawlerState import CrawlerState
from src.model.orm.OrmUtils import to_dict
from src.persistence.resources.abstract_classes.AbstractResource import AbstractResource


class CrawlerStateResource(AbstractResource):
    def get(self, user_id: int):
        session = self._create_session()
        state = session.query(CrawlerState).filter_by(user_id=user_id).first()
        if state is None:
            return 'Not found', 404
        state = to_dict(state)
        return jsonify(state)

    def put(self, user_id: int):
        session = self._create_session()
        data = request.json
        new_state = CrawlerState(user_id, **data)
        state = session.query(CrawlerState).filter_by(user_id=user_id).first()
        if state is not None:
            session.delete(state)
            session.flush()
        session.add(new_state)
        session.commit()

    def delete(self, user_id: int):
        session = self._create_session()
        session.query(CrawlerState).filter_by(user_id=user_id).delete()
        session.commit()

    def patch(self, user_id: int):
        session = self._create_session()
        data = request.json
        session.query(CrawlerState).filter_by(user_id=user_id).update(data)
        session.commit()
