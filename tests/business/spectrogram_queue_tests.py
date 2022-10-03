from queue import Queue

from config.constants import ID_FIELD_SIZE, SLICES_NUMBER_BYTES


def test1():
    with open('../auxiliary_files/spectrogram_from_python.png', 'rb') as f:
        spectrogram = f.read()
    q = Queue()
    song_id = 1
    song_id = song_id.to_bytes(ID_FIELD_SIZE, 'big', signed=False)
    slice_number = 1000
    for slice_index in range(slice_number):
        slice_index = slice_index.to_bytes(5, 'big', signed=False)
        q.put((song_id, slice_index, spectrogram))
    for _ in range(slice_number):
        new_song_id, _, new_spectrogram = q.get()
        print(f'{new_song_id is song_id} {new_spectrogram is spectrogram}')


if __name__ == '__main__':
    test1()
