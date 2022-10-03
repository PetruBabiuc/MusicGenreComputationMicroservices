from __future__ import annotations

from threading import RLock

from src.persistence.DatabaseManagerInterface import DatabaseManagerInterface


class DatabaseManagerStub(DatabaseManagerInterface):
    def __init__(self):
        self.__lock = RLock()
        self.__db: dict[tuple[int, str], str | None] = {(0, 'Melodie'): 'Electronic'}

    def get_song_genre(self, song: str) -> str | None:
        for pair, genre in self.__db.items():
            if pair[1] == song:
                return genre
        return None

    def insert_song_data_row(self, song: str) -> int:
        new_id = max(self.__db, key=lambda entry: entry[0])[0] + 1
        self.__db[(new_id, song)] = None
        return new_id

    def update_song_genre(self, song_id: int, genre: str) -> None:
        for id, song_name in self.__db.keys():
            if id == song_id:
                self.__db[(id, song_name)] = genre
                return

    def __enter__(self) -> DatabaseManagerInterface:
        self.__lock.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__lock.release()
