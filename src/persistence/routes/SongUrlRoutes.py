from http import HTTPStatus
from typing import Any

from classy_fastapi import get, post
from fastapi import Body, Depends, HTTPException
from functional import seq
from starlette.responses import JSONResponse, Response

import config.database_api as api_paths
from config.user_types import ADMIN, MICROSERVICE, USER
from src.helpers.ModelUtils import orm_to_dict
from src.model.orm.SongUrl import SongUrl
from src.persistence.routes.abstract_classes.AbstractRoutable import AbstractRoutable
from src.persistence.routes.abstract_classes.AbstractSecuredRoutable import AbstractSecuredRoutable


class SongUrlRoutes(AbstractSecuredRoutable):
    @get(api_paths.SONGS_URLS_PATH)
    def get_songs_urls(self, user_id: int, genre_id: int = None,
                       token: str = Depends(AbstractRoutable.OAUTH2_SCHEME)):
        payload = self._assert_has_user_type_in(token, [ADMIN, MICROSERVICE, USER])
        if payload['user_type_id'] == USER and payload['user_id'] != user_id:
            raise HTTPException(HTTPStatus.FORBIDDEN)

        session = self._create_session()
        query = session.query(SongUrl).filter_by(user_id=user_id)
        if genre_id is not None:
            query = query.filter_by(genre_id=genre_id)
        urls = query.all()
        urls = [orm_to_dict(url) for url in urls]
        for url in urls:
            del url['user_id']
            if genre_id is not None:
                del url['genre_id']
        return urls

    @get(api_paths.SONGS_URLS_COUNT_PATH)
    def get_songs_urls_count(self, user_id: int,
                             token: str = Depends(AbstractRoutable.OAUTH2_SCHEME)):
        self._assert_has_user_type(token, MICROSERVICE)

        session = self._create_session()
        count = session.query(SongUrl).filter_by(user_id=user_id).count()
        return {'count': count}

    @post(api_paths.SONGS_URLS_PATH)
    def post_song_url(self, user_id: int, body: dict[str, Any] = Body(),
                      token: str = Depends(AbstractRoutable.OAUTH2_SCHEME)):
        self._assert_has_user_type(token, MICROSERVICE)

        session = self._create_session()
        song_url = SongUrl(**body)
        song_url.user_id = user_id
        session.add(song_url)
        session.commit()
        return song_url

    @post(api_paths.SONGS_URLS_BULK_ADD_PATH)
    def bulk_add_songs_urls(self, user_id: int, songs_urls: dict[str, list[str]] = Body(),
                            token: str = Depends(AbstractRoutable.OAUTH2_SCHEME)):
        self._assert_has_user_type(token, MICROSERVICE)

        session = self._create_session()
        songs_urls = seq(songs_urls.items()) \
            .flat_map(lambda pair: [SongUrl(song_url=url, genre_id=int(pair[0]), user_id=user_id) for url in pair[1]])\
            .to_list()
        session.add_all(songs_urls)
        session.commit()
        songs_urls = [orm_to_dict(song_url) for song_url in songs_urls]
        for song_url in songs_urls:
            del song_url['user_id']
            del song_url['genre_id']
        return JSONResponse(songs_urls, status_code=HTTPStatus.OK)

    @post(api_paths.SONGS_URLS_BULK_DELETE_PATH)
    def bulk_delete_songs_urls(self, user_id: int, songs_urls_ids: list[int] = Body(),
                               token: str = Depends(AbstractRoutable.OAUTH2_SCHEME)):
        self._assert_has_user_type(token, MICROSERVICE)

        session = self._create_session()
        session.query(SongUrl)\
            .filter_by(user_id=user_id)\
            .filter(SongUrl.song_url_id.in_(songs_urls_ids))\
            .delete()
        session.commit()
        return Response(status_code=HTTPStatus.OK)
