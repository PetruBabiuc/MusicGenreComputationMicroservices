from flask import jsonify, request

from src.model.orm.Service import Service
from src.model.orm.Song import Song
from src.model.orm.OrmUtils import to_dict, query_multidict_to_orm
from src.persistence.resources.abstract_classes.AbstractResource import AbstractResource


class ServicesResource(AbstractResource):
    def get(self):
        session = self._create_session()
        kwargs = query_multidict_to_orm(request.args, Song)
        songs = session.query(Service).filter_by(**kwargs).all()
        songs = [to_dict(song) for song in songs]
        return jsonify(songs)
