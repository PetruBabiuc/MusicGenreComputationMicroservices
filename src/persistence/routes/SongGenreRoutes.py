from classy_fastapi import get

import config.database_api as api_paths
from src.model.orm.SongGenre import SongGenre
from src.persistence.routes.abstract_classes.AbstractRoutable import AbstractRoutable


class SongGenreRoutes(AbstractRoutable):
    @get(api_paths.SONGS_GENRES_PATH)
    def get_all_genres(self):
        session = self._create_session()
        genres = session.query(SongGenre).all()
        return genres
