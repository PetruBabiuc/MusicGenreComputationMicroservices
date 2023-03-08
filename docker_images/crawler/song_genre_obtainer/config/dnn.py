import os
try:
    import tensorflow
except ModuleNotFoundError:
    print('Module "tensorflow" was not found...')

os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
GENRES = ('Electronic', 'Folk', 'Hip-Hop', 'Instrumental', 'Pop', 'Rock')   # Order matters!
GENRES_NUMBER = len(GENRES)
# 61% Jamendo relu
ACTIVATION = 'relu'
DROP_OUT = 0.2

try:
    INITIALIZER_CREATOR = tensorflow.keras.initializers.GlorotUniform
except NameError:
    print('Tensorflow was not imported so the constant INITIALIZER_CREATOR was not initialized...')
