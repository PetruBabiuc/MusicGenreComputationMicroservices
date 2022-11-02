from flask import jsonify, request

from src.model.orm.OrmUtils import to_dict, query_multidict_to_orm
from src.model.orm.SongUrl import SongUrl
from src.persistence.resources.abstract_classes.AbstractResource import AbstractResource


class SongUrlResource(AbstractResource):
    def get(self):
        kwargs = query_multidict_to_orm(request.args, SongUrl)
        session = self._create_session()
        songs = session.query(SongUrl).filter_by(**kwargs).all()
        songs = [to_dict(url) for url in songs]
        for song in songs:
            del song['user_id']
            del song['song_url_id']
        return jsonify(songs)

    def post(self):
        session = self._create_session()
        data = request.json
        song = SongUrl(**data)
        session.add(song)
        session.commit()

    def delete(self):
        kwargs = query_multidict_to_orm(request.args, SongUrl)
        session = self._create_session()
        session.query(SongUrl).filter_by(kwargs).delete()
        session.commit()
