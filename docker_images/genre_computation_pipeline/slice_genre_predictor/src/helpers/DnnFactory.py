from tflearn import DNN
from tflearn.layers.conv import conv_2d, max_pool_2d
from tflearn.layers.core import input_data, dropout, fully_connected
from tflearn.layers.estimator import regression
from config.constants import SLICE_EDGE
from config.dnn import ACTIVATION, INITIALIZER_CREATOR, GENRES_NUMBER, DROP_OUT


class DnnFactory:
    @staticmethod
    def create_dnn(dnn_path: str) -> DNN:
        model = DnnFactory.__create_model()
        model.load(dnn_path)
        return model

    @staticmethod
    def __create_model() -> DNN:
        convnet = input_data(shape=[None, SLICE_EDGE, SLICE_EDGE, 1], name='input')

        convnet = conv_2d(convnet, 64, 2, activation=ACTIVATION, weights_init=INITIALIZER_CREATOR())
        convnet = max_pool_2d(convnet, 2)

        convnet = conv_2d(convnet, 128, 2, activation=ACTIVATION, weights_init=INITIALIZER_CREATOR())
        convnet = max_pool_2d(convnet, 2)

        convnet = conv_2d(convnet, 256, 2, activation=ACTIVATION, weights_init=INITIALIZER_CREATOR())
        convnet = max_pool_2d(convnet, 2)

        convnet = conv_2d(convnet, 512, 2, activation=ACTIVATION, weights_init=INITIALIZER_CREATOR())
        convnet = max_pool_2d(convnet, 2)

        convnet = fully_connected(convnet, 1024, activation=ACTIVATION)

        convnet = dropout(convnet, DROP_OUT)

        convnet = fully_connected(convnet, GENRES_NUMBER, activation='softmax')
        convnet = regression(convnet, optimizer='rmsprop', loss='categorical_crossentropy')

        model = DNN(convnet)
        return model
