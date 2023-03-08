from typing import Callable

from classy_fastapi import post
from fastapi import Depends, Form, File, UploadFile, HTTPException
from starlette import status
from starlette.responses import JSONResponse
from starlette.status import HTTP_201_CREATED

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

    # TODO: Add constraints to name and author
    @post(controller.SONGS_PATH)
    def post_song(self, name: str = Form(), author: str = Form(),
                  song: UploadFile = File(),
                  token: str = Depends(AbstractSecuredRoutable.OAUTH2_SCHEME)):
        self.__db_api_proxy.validate_jwt(token)
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

        return JSONResponse(message, HTTP_201_CREATED)
