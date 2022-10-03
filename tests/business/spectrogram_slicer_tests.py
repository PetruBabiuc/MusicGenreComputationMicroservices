from io import BytesIO

from PIL import Image

from config.constants import SLICE_EDGE


def test1():
    with open('../auxiliary_files/spectrogram_from_python.png', 'rb') as f:
        spectrogram = f.read()
    spectrogram = BytesIO(spectrogram)
    spectrogram = Image.open(spectrogram)
    spectrogram = spectrogram.crop((0, 1, 128, 129))
    spectrogram_bytes = BytesIO()
    spectrogram.save(spectrogram_bytes, 'PNG')
    spectrogram_bytes = spectrogram_bytes.getvalue()
    with open('../auxiliary_files/spectrogram_slice_new.png', 'wb') as f:
        f.write(spectrogram_bytes)


def test2():
    with open('../auxiliary_files/spectrogram_from_python.png', 'rb') as f:
        spectrogram = f.read()
    spectrogram = BytesIO(spectrogram)
    spectrogram = Image.open(spectrogram)
    for i in range(11):
        left = i * SLICE_EDGE
        top = 1
        right = left + SLICE_EDGE
        bottom = SLICE_EDGE + 1
        spectrogram_bytes = BytesIO()
        spectrogram.crop((left, top, right, bottom)).save(spectrogram_bytes, 'PNG')

        with open(f'../auxiliary_files/30s_mono_slices/spectrogram_{i}_new.png', 'wb') as f:
            f.write(spectrogram_bytes.getvalue())


def test3():
    for i in range(11):
        with open(f'../auxiliary_files/30s_mono_slices/spectrogram_{i}.png', 'rb') as f:
            old = f.read()
        with open(f'../auxiliary_files/30s_mono_slices/spectrogram_{i}_new.png', 'rb') as f:
            new = f.read()
        print(old == new)  # :)


def test4():
    with open('../auxiliary_files/spectrogram_from_python.png', 'rb') as f:
        spectrogram = f.read()
    spectrogram = BytesIO(spectrogram)
    spectrogram = Image.open(spectrogram)
    for i in range(11):
        left = i * SLICE_EDGE
        top = 1
        right = left + SLICE_EDGE
        bottom = SLICE_EDGE + 1
        spectrogram = spectrogram.crop((left, top, right, bottom))
        spectrogram_bytes = spectrogram.tobytes()
        with open(f'../auxiliary_files/30s_mono_slices/spectrogram_{i}_new2.png', 'wb') as f:
            f.write(spectrogram_bytes)


if __name__ == '__main__':
    test4()
