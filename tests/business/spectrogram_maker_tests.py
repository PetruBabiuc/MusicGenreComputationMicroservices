import shlex
from io import BytesIO
from multiprocessing import Pipe
from subprocess import Popen, PIPE
import sox
from pydub import AudioSegment
from src.business.SpectrogramMaker import SpectrogramMaker
from mutagen.mp3 import MP3, MPEGInfo


def test1():
    with open('../auxiliary_files/MonoSong.mp3', 'rb') as f:
        song_data = f.read()
    song_data = BytesIO(song_data)
    song = AudioSegment.from_mp3(song_data)
    print(song.channels)
    song.set_channels()
    pass


def test2():
    with open('../auxiliary_files/MonoSong.mp3', 'rb') as f:
        song_data = f.read()
    song_data = BytesIO(song_data)
    # Doesn't work, it wants just filepaths, not opened files / filelike objects...
    # song = eyed3.load(song_data)
    pass


def test3():
    with open('../auxiliary_files/StereoSong.mp3', 'rb') as f:
        song_data = f.read()
    song_data = SpectrogramMaker.down_mix_to_mono(song_data)
    with open('../auxiliary_files/NewMonoSong.mp3', 'wb') as f:
        f.write(song_data)


def test4():
    with open('../auxiliary_files/StereoSong.mp3', 'rb') as f:
        song_data = f.read()
    song_data = BytesIO(song_data)
    f = MP3(song_data)
    bitrate = f.info.bitrate // 1000
    channels = f.info.channels
    pass


def get_song_info(song: bytes) -> MPEGInfo:
    song = BytesIO(song)
    song = MP3(song)
    return song.info


def down_mix_to_mono(song: bytes, bitrate: int) -> bytes:
    command = f'sox -t mp3 - -t mp3 -C {bitrate}.05 - remix -'
    command = shlex.split(command)
    p = Popen(command, stdin=PIPE, stdout=PIPE)
    output, errors = p.communicate(song)
    if errors:
        print(errors)
    return output


def create_spectrogram(song: bytes) -> bytes:
    song_info = get_song_info(song)
    if song_info.channels > 1:
        song = down_mix_to_mono(song, song_info.bitrate // 1000)
    return song


def test5():
    with open('../auxiliary_files/StereoSong.mp3', 'rb') as f:
        song_data = f.read()
    song_data = create_spectrogram(song_data)
    with open('../auxiliary_files/NewMonoSong.mp3', 'wb') as f:
        f.write(song_data)


def test6():
    with open('../auxiliary_files/NewMonoSong.mp3', 'rb') as f:
        song_data = f.read()
    spectrogram = SpectrogramMaker.__create_spectrogram(song_data, 1, 283)
    with open('../auxiliary_files/spectrogram.png', 'wb') as f:
        f.write(spectrogram)


def test7():
    with open('../auxiliary_files/FirstProjectMixDown.mp3', 'rb') as f:
        first = f.read()
    with open('../auxiliary_files/NewMonoSong.mp3', 'rb') as f:
        second = f.read()
    pass


def test8():
    first = AudioSegment.from_mp3('../auxiliary_files/FirstProjectMixDownV2.mp3')
    second = AudioSegment.from_mp3('../auxiliary_files/NewMonoSong.mp3')
    matches = 0
    for i in range(len(first.raw_data)):
        if first.raw_data[i] == second.raw_data[i]:
            matches += 1
        else:
            print('#' * 10 + ' NOT OK! ' + '#' * 10)
    ratio = matches / len(first.raw_data)
    print(ratio)
    pass


def test9():
    with open('../auxiliary_files/StereoSong.mp3', 'rb') as f:
        song_data = f.read()
    command1 = 'sox -t mp3 - -t mp3 -C 236.05 - remix -'
    command1 = shlex.split(command1)
    command2 = 'sox -t mp3 - -n spectrogram -Y 200 -X 50 -m -r -o -'
    command2 = shlex.split(command2)
    p1 = Popen(command1, stdin=PIPE, stdout=PIPE)
    p2 = Popen(command2, stdin=p1.stdout, stdout=PIPE)
    output, error = p1.communicate(song_data)
    output, error = p2.communicate()
    with open('../auxiliary_files/spectrogram.png', 'wb') as f:
        f.write(output)


def test10():
    with open('../auxiliary_files/StereoSong.mp3', 'rb') as f:
        song_data = f.read()
    command = 'sox -t mp3 - -n remix - spectrogram -X 50 -Y 200 -m -r -d 283 -o -'
    command = shlex.split(command)
    p = Popen(command, stdin=PIPE, stdout=PIPE)
    output, error = p.communicate(song_data)
    with open('../auxiliary_files/spectrogram_from_python.png', 'wb') as f:
        f.write(output)

def test11():
    with open('../auxiliary_files/MonoSong.mp3', 'rb') as f:
        song_data = f.read()
    command = 'sox -t mp3 - -n spectrogram -X 50 -Y 200 -m -r -d 30 -o -'
    command = shlex.split(command)
    p = Popen(command, stdin=PIPE, stdout=PIPE)
    output, errors = p.communicate(song_data)
    with open('../auxiliary_files/spectrogram_from_python.png', 'wb') as f:
        f.write(output)

def test12():
    command = "sox '../auxiliary_files/MonoSong.mp3' -n spectrogram -Y 200 -X 50 -m -r -d 30 -o -"
    command = shlex.split(command)
    p = Popen(command, stdout=PIPE)
    output, errors = p.communicate()
    with open('../auxiliary_files/spectrogram_from_python.png', 'wb') as f:
        f.write(output)

def test13():
    command = "sox '../auxiliary_files/MonoDownMix.mp3' -n spectrogram -Y 200 -X 50 -m -r -d 283 -o -"
    command = shlex.split(command)
    p = Popen(command, stdout=PIPE)
    output, errors = p.communicate()
    with open('../auxiliary_files/spectrogram_from_python.png', 'wb') as f:
        f.write(output)


def test14():
    with open('../auxiliary_files/StereoSong.mp3', 'rb') as f:
        song_data = f.read()
    spectrogram = SpectrogramMaker.__create_spectrogram(song_data, 2, 283)
    with open('../auxiliary_files/spectrogram_from_python.png', 'wb') as f:
        f.write(spectrogram)

def test15():
    with open('../auxiliary_files/MonoSong.mp3', 'rb') as f:
        song_data = f.read()
    spectrogram = SpectrogramMaker.__create_spectrogram(song_data, 1, 30)
    with open('../auxiliary_files/spectrogram_from_python.png', 'wb') as f:
        f.write(spectrogram)

if __name__ == '__main__':
    test5()
