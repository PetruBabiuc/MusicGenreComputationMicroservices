from http import HTTPStatus
from typing import Any

from classy_fastapi import get, patch, post, delete
from fastapi import Body, Depends, HTTPException
from starlette.responses import JSONResponse

import config.database_api as api_paths
from config.user_types import USER, MICROSERVICE
from src.helpers.ModelUtils import orm_to_dict
from src.model.orm.Song import Song
from src.model.orm.SongInfo import SongInfo
from src.presentation.abstract_classes.routes.AbstractSecuredDatabaseApiRoutable import AbstractSecuredDatabaseApiRoutable


class SongRoutes(AbstractSecuredDatabaseApiRoutable):
    @post(api_paths.SONGS_PATH)
    def post_song(self, body: dict[str, Any] = Body(),
                  token: str = Depends(AbstractSecuredDatabaseApiRoutable.OAUTH2_SCHEME)):
        self._jwt_manager.assert_has_user_type(token, MICROSERVICE)

        session = self._create_session()

        song_info = None
        if 'song_info' in body:
            song_info = body['song_info']
            del body['song_info']

        song = Song(**body)
        session.add(song)
        session.flush()

        if song_info is not None:
            song.song_info = SongInfo(song.song_id, **song_info)
            session.flush()

        session.commit()
        return JSONResponse(orm_to_dict(song), status_code=HTTPStatus.CREATED)

    @get(api_paths.SONG_BY_ID_PATH)
    def get_song_by_id(self, song_id: int,
                       token: str = Depends(AbstractSecuredDatabaseApiRoutable.OAUTH2_SCHEME)):
        payload = self._jwt_manager.assert_has_user_type_in(token, [USER, MICROSERVICE])

        session = self._create_session()
        song: Song = session.get(Song, song_id)

        if song is None:
            raise HTTPException(HTTPStatus.NOT_FOUND)

        if payload['user_type_id'] == USER and song.user_id != payload['user_id']:
            raise HTTPException(HTTPStatus.FORBIDDEN)

        return song.to_dict()

    @get(api_paths.SONGS_OF_USER)
    def get_songs_of_user(self, user_id: int, token: str = Depends(AbstractSecuredDatabaseApiRoutable.OAUTH2_SCHEME)):
        payload = self._jwt_manager.assert_has_user_type(token, USER)

        if payload['user_id'] != user_id:
            raise HTTPException(HTTPStatus.FORBIDDEN)

        session = self._create_session()
        songs = session.query(Song).filter_by(user_id=user_id).all()
        songs = [song.to_dict() for song in songs]

        return songs

    @patch(api_paths.SONG_BY_ID_PATH)
    def patch_song_by_id(self, song_id: int, body: dict[str, Any] = Body(),
                         token: str = Depends(AbstractSecuredDatabaseApiRoutable.OAUTH2_SCHEME)):
        payload = self._jwt_manager.assert_has_user_type_in(token, [MICROSERVICE, USER])

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
    def delete_song(self, song_id: int, token: str = Depends(AbstractSecuredDatabaseApiRoutable.OAUTH2_SCHEME)):
        payload = self._jwt_manager.assert_has_user_type(token, USER)

        session = self._create_session()
        song: Song = session.get(Song, song_id)

        if song is None:
            raise HTTPException(HTTPStatus.NOT_FOUND)

        if song.user_id != payload['user_id']:
            raise HTTPException(HTTPStatus.FORBIDDEN)

        session.delete(song)
        session.commit()
