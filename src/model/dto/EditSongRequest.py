from pydantic import BaseModel, constr, conint

from config.dnn import GENRES


class EditSongRequest(BaseModel):
    song_name: constr(min_length=1, max_length=30)
    author: constr(min_length=1, max_length=30)
    genre_id: conint(ge=1, le=len(GENRES))
