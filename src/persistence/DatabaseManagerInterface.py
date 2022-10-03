from __future__ import annotations
from abc import ABCMeta, abstractmethod


class DatabaseManagerInterface(metaclass=ABCMeta):
    @abstractmethod
    def get_song_genre(self, song: str) -> str | None:
        pass

    @abstractmethod
    def insert_song_data_row(self, song: str) -> int:
        pass

    @abstractmethod
    def update_song_genre(self, song_id: int, genre: str) -> None:
        pass
