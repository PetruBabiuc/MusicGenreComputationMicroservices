from typing import Any

from classy_fastapi import get, patch, post
from fastapi import Body
from starlette import status
from starlette.responses import Response, JSONResponse

import config.database_api as api_paths
from src.helpers.ModelUtils import orm_to_dict
from src.model.orm.Song import Song
from src.persistence.routes.abstract_classes.AbstractRoutable import AbstractRoutable


class SongRoutes(AbstractRoutable):
    @post(api_paths.SONGS_PATH)
    def post_song(self, body: dict[str, Any] = Body()):
        session = self._create_session()
        song = Song(**body)
        session.add(song)
        session.flush()
        session.commit()
        return JSONResponse(orm_to_dict(song), status_code=status.HTTP_201_CREATED)

    @get(api_paths.SONG_BY_ID_PATH)
    def get_song_by_id(self, song_id: int):
        session = self._create_session()
        song = session.get(Song, song_id)
        if song is None:
            return Response(status_code=status.HTTP_404_NOT_FOUND)
        return song

    @patch(api_paths.SONG_BY_ID_PATH)
    def patch_song_by_id(self, song_id: int, body: dict[str, Any] = Body()):
        session = self._create_session()
        query = session.query(Song).filter_by(song_id=song_id)
        if query.count() == 0:
            return Response(status_code=status.HTTP_404_NOT_FOUND)
        query.update(body)
        session.commit()
        return Response(status_code=status.HTTP_200_OK)
