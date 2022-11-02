from flask import jsonify, request

from src.model.orm.Song import Song
from src.model.orm.OrmUtils import to_dict, query_multidict_to_orm
from src.persistence.resources.abstract_classes.AbstractResource import AbstractResource


class SongResource(AbstractResource):
    def get(self):
        session = self._create_session()
        kwargs = query_multidict_to_orm(request.args, Song)
        songs = session.query(Song).filter_by(**kwargs).all()
        songs = [to_dict(song) for song in songs]
        return jsonify(songs)

    def post(self):
        session = self._create_session()
        data = request.json
        song = Song(**data)
        session.add(song)
        session.commit()
        return jsonify({'song_id': song.song_id})

    def patch(self):
        session = self._create_session()
        kwargs = query_multidict_to_orm(request.args, Song)
        data = request.json
        session.query(Song).filter_by(**kwargs).update(data)
        session.commit()
