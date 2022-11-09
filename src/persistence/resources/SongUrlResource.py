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
        return jsonify(songs)

    def post(self):
        session = self._create_session()
        if request.args.get('bulk', False):
            genre_id = request.json['genre_id']
            user_id = request.json['user_id']
            urls = request.json['urls']
            song_urls = [SongUrl(song_url=url, user_id=user_id, genre_id=genre_id) for url in urls]
            session.add_all(song_urls)
        else:
            data = request.json
            song = SongUrl(**data)
            session.add(song)
        session.commit()

    def delete(self):
        session = self._create_session()
        if request.args.get('bulk', False):
            session.query(SongUrl).filter(SongUrl.song_url_id.in_(request.json)).delete()
        else:
            kwargs = query_multidict_to_orm(request.args, SongUrl)
            session.query(SongUrl).filter_by(**kwargs).delete()
        session.commit()
