from io import BytesIO

from PIL import Image

from config.constants import SLICE_EDGE


def test1():
    with open('../auxiliary_files/spectrogram_from_python.png', 'rb') as f:
        spectrogram = f.read()
    spectrogram = BytesIO(spectrogram)
    img = Image.open(spectrogram)
    slices_number = img.width // SLICE_EDGE
    pass

if __name__ == '__main__':
    test1()
