from pathlib import Path
from typing import Callable

from classy_fastapi import post, get, delete
from fastapi import Depends, Form, File, UploadFile, HTTPException
from starlette import status
from starlette.responses import JSONResponse, FileResponse
from starlette.status import HTTP_201_CREATED, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR

import config.song_adder_controller as controller
from config.database_api_credentials import MICROSERVICE_CREDENTIALS
from config.user_types import USER
from src.helpers.DatabaseApiProxy import DatabaseApiProxy
from src.presentation.abstract_classes.routes.AbstractSecuredRoutable import AbstractSecuredRoutable


class SongRoutes(AbstractSecuredRoutable):
    def __init__(self, mp3_validator_func: Callable[[int, bytes], bool],
                 compute_genre_func: Callable[[int, bytes], dict]):
        super().__init__()

        self.__compute_genre_func = compute_genre_func
        self.__mp3_validator_func = mp3_validator_func

        self.__db_api_proxy = DatabaseApiProxy(*MICROSERVICE_CREDENTIALS)
        genres = self.__db_api_proxy.get_genres()
        self.__genre_name_to_id = {genre['song_genre_name']: genre['song_genre_id'] for genre in genres}

    @post(controller.SONGS_PATH)
    def post_song(self, name: str = Form(min_length=1, max_length=30),
                  author: str = Form(min_length=1, max_length=30),
                  song: UploadFile = File(),
                  token: str = Depends(AbstractSecuredRoutable.OAUTH2_SCHEME)):
        if not self.__db_api_proxy.validate_jwt(token):
            raise HTTPException(HTTP_403_FORBIDDEN)

        jwt_payload = self._jwt_manager.assert_has_user_type(token, USER)

        genre_id = self.__genre_name_to_id['Computing...']
        user_id = jwt_payload['user_id']
        # TODO: Dynamically get MP3's format ID
        response = self.__db_api_proxy.post_song(user_id, name, genre_id, author, 1)
        song_id = response.json()['song_id']

        song_bytes = song.file.read()
        if not self.__mp3_validator_func(song_id, song_bytes):
            self.__db_api_proxy.delete_song(song_id)
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY,
                                'Invalid MP3 song! It may have inappropriate length or encoding problems.')

        message = self.__compute_genre_func(song_id, song_bytes)

        with open(f'{controller.SONGS_STORAGE_PATH}/{song_id}', 'wb') as f:
            f.write(song_bytes)

        return JSONResponse(message, HTTP_201_CREATED)

    @get(controller.SONG_BY_ID_PATH)
    def get_song(self, song_id: int, token: str = Depends(AbstractSecuredRoutable.OAUTH2_SCHEME)):
        self.__assert_user_can_manage_song(token, song_id)

        song_path = f'{controller.SONGS_STORAGE_PATH}/{song_id}'
        if not Path.is_file(Path(song_path)):
            raise HTTPException(HTTP_500_INTERNAL_SERVER_ERROR, 'The song appears in the database but its file '
                                                                'was not found in the song storage...')

        return FileResponse(song_path, media_type='audio/*')

    @delete(controller.SONG_BY_ID_PATH)
    def delete_song(self, song_id: int, token: str = Depends(AbstractSecuredRoutable.OAUTH2_SCHEME)):
        self.__assert_user_can_manage_song(token, song_id)

        self.__db_api_proxy.delete_song(song_id)
        Path(f'{controller.SONGS_STORAGE_PATH}/{song_id}').unlink(missing_ok=True)

    def __assert_user_can_manage_song(self, jwt: str, song_id: int) -> None:
        if not self.__db_api_proxy.validate_jwt(jwt):
            raise HTTPException(HTTP_403_FORBIDDEN)
        jwt_payload = self._jwt_manager.assert_has_user_type(jwt, USER)

        try:
            user_id = self.__db_api_proxy.get_song_by_id(song_id)['user_id']
        except KeyError as ex:
            raise HTTPException(HTTP_404_NOT_FOUND)

        if user_id != jwt_payload['user_id']:
            raise HTTPException(HTTP_403_FORBIDDEN)