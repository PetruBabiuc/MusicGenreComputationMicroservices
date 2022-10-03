from numpy import argmax
from config.constants import SLICE_EDGE
from config.dnn import GENRES
from src.helpers.DnnFactory import DnnFactory
from src.helpers.ImageTransformer import ImageTransformer


def test1():
    dnn = DnnFactory.create_dnn('../../dnn/musicDNN.tflearn')
    for i in range(11):
        with open(f'../auxiliary_files/30s_mono_slices/spectrogram_{i}.png', 'rb') as f:
            image = f.read()
        image = ImageTransformer.transform_image(image, SLICE_EDGE)
        image = [image]
        res = dnn.predict(image)[0]
        max_ind = argmax(res)
        max_prob = res[max_ind]
        genre = GENRES[max_ind]
        print(f'Slice {i} => Genre: {genre}, prob: {max_prob}')


if __name__ == '__main__':
    test1()
