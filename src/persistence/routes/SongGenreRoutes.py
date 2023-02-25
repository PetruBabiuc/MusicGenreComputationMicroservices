from classy_fastapi import get

import config.database_api as api_paths
from src.model.orm.SongGenre import SongGenre
from src.presentation.abstract_classes.routes.AbstractDatabaseApiRoutable import AbstractDatabaseApiRoutable


class SongGenreRoutes(AbstractDatabaseApiRoutable):
    @get(api_paths.SONGS_GENRES_PATH)
    def get_all_genres(self):
        session = self._create_session()
        genres = session.query(SongGenre).all()
        return genres
