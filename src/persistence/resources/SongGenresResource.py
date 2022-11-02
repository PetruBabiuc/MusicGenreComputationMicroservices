from flask import jsonify, request

from src.model.orm.OrmUtils import to_dict, query_multidict_to_orm
from src.model.orm.SongGenre import SongGenre
from src.persistence.resources.abstract_classes.AbstractResource import AbstractResource


class SongGenresResource(AbstractResource):
    def get(self):
        kwargs = query_multidict_to_orm(request.args, SongGenre)
        session = self._create_session()
        song_genres = session.query(SongGenre).filter_by(**kwargs).all()
        song_genres = [to_dict(url) for url in song_genres]
        return jsonify(song_genres)
