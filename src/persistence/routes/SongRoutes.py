from http import HTTPStatus
from typing import Any

from classy_fastapi import get, patch, post, delete
from fastapi import Body, Depends, HTTPException
from starlette.responses import JSONResponse

import config.database_api as api_paths
from config.user_types import USER, MICROSERVICE
from src.helpers.ModelUtils import orm_to_dict
from src.model.orm.Song import Song
from src.persistence.routes.abstract_classes.AbstractRoutable import AbstractRoutable
from src.persistence.routes.abstract_classes.AbstractSecuredRoutable import AbstractSecuredRoutable


class SongRoutes(AbstractSecuredRoutable):
    @post(api_paths.SONGS_PATH)
    def post_song(self, body: dict[str, Any] = Body(),
                  token: str = Depends(AbstractRoutable.OAUTH2_SCHEME)):
        self._assert_has_user_type(token, MICROSERVICE)

        session = self._create_session()
        song = Song(**body)
        session.add(song)
        session.flush()
        session.commit()
        return JSONResponse(orm_to_dict(song), status_code=HTTPStatus.CREATED)

    @get(api_paths.SONG_BY_ID_PATH)
    def get_song_by_id(self, song_id: int, token: str = Depends(AbstractRoutable.OAUTH2_SCHEME)):
        payload = self._assert_has_user_type_in(token, [USER, MICROSERVICE])

        session = self._create_session()
        song = session.get(Song, song_id)

        if song is None:
            raise HTTPException(HTTPStatus.NOT_FOUND)

        if payload['user_type_id'] == USER and song.user_id != payload['user_id']:
            raise HTTPException(HTTPStatus.FORBIDDEN)

        return song

    @patch(api_paths.SONG_BY_ID_PATH)
    def patch_song_by_id(self, song_id: int, body: dict[str, Any] = Body(),
                         token: str = Depends(AbstractRoutable.OAUTH2_SCHEME)):
        payload = self._assert_has_user_type_in(token, [MICROSERVICE, USER])

        session = self._create_session()
        query = session.query(Song).filter_by(song_id=song_id)
        if query.count() == 0:
            raise HTTPException(HTTPStatus.NOT_FOUND)

        song = query.first()
        if payload['user_type_id'] == USER and payload['user_id'] != song.user_id:
            raise HTTPException(HTTPStatus.FORBIDDEN)

        query.update(body)
        session.commit()

    @delete(api_paths.SONG_BY_ID_PATH)
    def delete_song(self, song_id: int, token: str = Depends(AbstractRoutable.OAUTH2_SCHEME)):
        payload = self._assert_has_user_type(token, USER)

        session = self._create_session()
        song: Song = session.get(Song, song_id)

        if song is None:
            raise HTTPException(HTTPStatus.NOT_FOUND)

        if song.user_id != payload['user_id']:
            raise HTTPException(HTTPStatus.FORBIDDEN)

        session.delete(song)
        session.commit()
