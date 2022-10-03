import glob
import os.path
import time
from socket import socket, SOCK_STREAM, AF_INET
from threading import Thread
from config.controller import CLIENT_PORT, HOST
from src.helpers.HighLevelSocketWrapper import HighLevelSocketWrapper


def time_it(func):
    def wrapper(*args, **kwargs):
        begin = time.time()
        output = func(*args, **kwargs)
        end = time.time()
        print(f'Total time taken by {func.__name__}: {end - begin}')
        return output

    return wrapper


def request_song_genre(song_path: str):
    # Connecting...
    client_socket = HighLevelSocketWrapper(socket(AF_INET, SOCK_STREAM))
    client_socket.connect((HOST, CLIENT_PORT))

    song_name = os.path.basename(song_path)
    # Requesting song's genre
    message = {'song_name': song_name}
    client_socket.send_dict_as_json(message)

    # Receiving genre
    message = client_socket.receive_json_as_dict()
    # print(f'{song_name} => Response from Controller: {message}')

    if message['genre'] is not None:
        return

    # print(f"{song_name} => Song's bytes' number: {os.path.getsize(song_path)}")
    client_socket.sendfile(song_path)

    message = client_socket.receive_json_as_dict()
    print(f'{song_name} => Response from Controller: {message}')
    client_socket.close()


def test1():
    song_path = '../../../DeepAudioClassification-master/Data/Raw/petru/[YT2mp3.info] - Lil Jon & The East Side Boyz - Get Low (feat. Ying Yang Twins) (Official Music Video) (320kbps).mp3'
    request_song_genre(song_path)


@time_it
def test2():
    path = '../../../DeepAudioClassification-master/Data/Raw/petru'
    path = os.path.join(path, '**/*.mp3')
    song_paths = glob.glob(path, recursive=True)
    threads = [Thread(target=request_song_genre, args=(song_path,))
               for i, song_path in enumerate(song_paths)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()


def test3():
    with open('../../../DeepAudioClassification-master/Data/Raw/free_mp3/Air_(Bach)_-_Aurbanni.mp3', 'rb') as f:
        bytes_number_1 = len(f.read())
    bytes_number_2 = os.path.getsize('../../../'
                                     'DeepAudioClassification-master/Data/Raw/free_mp3/Air_(Bach)_-_Aurbanni.mp3')
    print(bytes_number_1, bytes_number_2)


if __name__ == '__main__':
    test1()
