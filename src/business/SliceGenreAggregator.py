from queue import Queue
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
from typing import Callable
from config import slice_genre_aggregator, controller
from config.constants import ID_FIELD_SIZE
from src.AbstractMicroservice import AbstractMicroservice
from src.helpers.HighLevelSocketWrapper import HighLevelSocketWrapper
from src.helpers.SynchronizedDict import SynchronizedDict
from src.model.SongGenresPack import SongGenresPack


class SliceGenreAggregator(AbstractMicroservice):
    def __init__(self, name: str = 'SliceGenreAggregator', log_func: Callable[[str], None] = print):
        super().__init__(name, log_func)

        self.__slices_number_socket = HighLevelSocketWrapper(socket(AF_INET, SOCK_STREAM))
        self.__slices_number_socket.bind((slice_genre_aggregator.HOST, slice_genre_aggregator.SLICE_NUMBER_PORT))
        self.__slices_number_socket.listen()
        self._log_func(f'[{self._name}] Slices number aggregation ServerSocket opened on '
                       f'{slice_genre_aggregator.HOST}:{slice_genre_aggregator.SLICE_NUMBER_PORT}!')

        self.__slices_genre_socket = HighLevelSocketWrapper(socket(AF_INET, SOCK_STREAM))
        self.__slices_genre_socket.bind((slice_genre_aggregator.HOST, slice_genre_aggregator.SLICE_GENRE_PORT))
        self.__slices_genre_socket.listen()
        self._log_func(f'[{self._name}] Slices genre aggregation ServerSocket opened on '
                       f'{slice_genre_aggregator.HOST}:{slice_genre_aggregator.SLICE_GENRE_PORT}!')

        self.__song_id_to_genres_package: SynchronizedDict[bytes, SongGenresPack] = SynchronizedDict()
        self.__genres_to_compute_queue: Queue[tuple[bytes, dict[str, int]]] = Queue()

    def __aggregate_slices_number(self, client_socket: HighLevelSocketWrapper, addr: tuple[str, int]) -> None:
        message = client_socket.receive_message()

        song_id = message[:ID_FIELD_SIZE]
        # song_id = int.from_bytes(song_id, 'big', signed=False)

        slices_number = message[ID_FIELD_SIZE:]
        slices_number = int.from_bytes(slices_number, 'big', signed=False)

        self._log_func(f'[{self._name}] Slices number aggregated:'
                       f'\n\tClient: {addr}'
                       f'\n\tSongID: {song_id}'
                       f'\n\tSlices number:{slices_number}')
        with self.__song_id_to_genres_package as d:
            d[song_id] = SongGenresPack(slices_number)
        client_socket.close()

    def __aggregate_slice_genre(self, client_socket: HighLevelSocketWrapper, addr: tuple[str, int]) -> None:
        message = client_socket.receive_message()

        song_id = message[:ID_FIELD_SIZE]
        # song_id = int.from_bytes(song_id, 'big', signed=False)

        genre = message[ID_FIELD_SIZE:]
        genre = genre.decode()

        with self.__song_id_to_genres_package as d:
            if song_id in d:
                package = d[song_id]
                package.remaining_slices -= 1
                if genre in package.genres_to_counts:
                    package.genres_to_counts[genre] += 1
                else:
                    package.genres_to_counts[genre] = 1
                if package.remaining_slices == 0:
                    self.__genres_to_compute_queue.put((song_id, package.genres_to_counts))
                    del d[song_id]
                self._log_func(f'[{self._name}] Slice genre aggregated:'
                               f'\n\tClient: {addr}'
                               f'\n\tSongID: {song_id}'
                               f'\n\tGenre: {genre}'
                               f'\n\tRemaining slices: {package.remaining_slices}')
            else:
                self._log_func(f'[{self._name}] Error: Trying to aggregate '
                               f'slice genre to a song which has no entry in the dictionary...')
        client_socket.close()

    def __aggregate_slices_number_task(self) -> None:
        while True:
            client_socket, addr = self.__slices_number_socket.accept()
            Thread(target=self.__aggregate_slices_number, args=(client_socket, addr)).start()

    def __aggregate_slices_genre_task(self) -> None:
        while True:
            client_socket, addr = self.__slices_genre_socket.accept()
            Thread(target=self.__aggregate_slice_genre, args=(client_socket, addr)).start()

    def __compute_genre_task(self):
        while True:
            song_id, genres_to_counts = self.__genres_to_compute_queue.get()
            genre, count = max(genres_to_counts.items(), key=lambda it: it[1])
            slices_number = sum(genres_to_counts.values())
            self._log_func(f'[{self._name}] Genre computed:'
                           f'\n\tSongID: {song_id}'
                           f'\n\tGenre: {genre}'
                           f'\n\tSlices with the predominant genre: {count} / {slices_number}'
                           f'\n\tRatio: {count / slices_number}')
            self.__send_result_to_controller(song_id, genre)
            self.__send_result_to_db(song_id, genre)

    @staticmethod
    def __send_result_to_controller(song_id: bytes, genre: str) -> None:
        song_id = int.from_bytes(song_id, 'big', signed=False)
        message = {'song_id': song_id, 'genre': genre}

        client_socket = HighLevelSocketWrapper(socket(AF_INET, SOCK_STREAM))
        client_socket.connect((controller.HOST, controller.RESULTS_PORT))
        client_socket.send_dict_as_json(message)
        client_socket.close()

    def __send_result_to_db(self, song_id: bytes, genre: str):
        pass

    def run(self) -> None:
        Thread(target=self.__aggregate_slices_number_task).start()
        Thread(target=self.__compute_genre_task).start()
        self.__aggregate_slices_genre_task()


if __name__ == '__main__':
    SliceGenreAggregator().run()
