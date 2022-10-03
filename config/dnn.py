import os
import tensorflow

os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
GENRES = ('Electronic', 'Folk', 'Hip-Hop', 'Instrumental', 'Pop', 'Rock')   # Order matters!
GENRES_NUMBER = len(GENRES)
# 61% Jamendo relu
ACTIVATION = 'relu'
DROP_OUT = 0.2
INITIALIZER_CREATOR = tensorflow.keras.initializers.GlorotUniform
