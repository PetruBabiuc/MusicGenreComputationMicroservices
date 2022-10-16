import glob
import os.path
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread

from config.constants import ID_FIELD_SIZE
from config.crawler_genre_obtainer import HOST as OBTAINER_HOST, URL_PROCESSOR_PORT as OBTAINER_PORT
from src.helpers.HighLevelSocketWrapper import HighLevelSocketWrapper


def test_song_genre_obtainer(path: str, client_id: int):
    with open(path, 'rb') as f:
        song = f.read()

    client_id = client_id.to_bytes(ID_FIELD_SIZE, 'big', signed=False)

    message = client_id + song

    con = HighLevelSocketWrapper(socket(AF_INET, SOCK_STREAM))
    con.connect((OBTAINER_HOST, OBTAINER_PORT))
    con.send_message(message)

    message = con.receive_json_as_dict()
    con.close()

    print(f'{os.path.basename(path)} => {message}')


def test1():
    song_path = '/home/petru/Licenta/DeepAudioClassification-master/Data/Raw/free_mp3/Air_(Bach)_-_Aurbanni.mp3'
    test_song_genre_obtainer(song_path, 100)


def test2():
    song_path = '/home/petru/Licenta/DeepAudioClassification-master/Data/Raw/dataset/00/1100.mp3'
    test_song_genre_obtainer(song_path, 200)


def test3():
    paths = glob.glob('/home/petru/Licenta/DeepAudioClassification-master/Data/Raw/dataset/00/*.mp3')[:30]
    threads = [Thread(target=test_song_genre_obtainer, args=(path, index)) for index, path in enumerate(paths)]
    for t in threads:
        t.start()

    for t in threads:
        t.join()


if __name__ == '__main__':
    test3()
