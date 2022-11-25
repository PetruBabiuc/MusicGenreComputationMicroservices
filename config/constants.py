ID_FIELD_SIZE = 4
PIXELS_PER_SECOND = 50
SLICE_EDGE = 128
SLICES_NUMBER_BYTES = 1
LOGGED_URLS = 2
REQUEST_TIMEOUT = 10
MIN_SONG_LENGTH = 30

# 2 ^ (8 * NUMBER_OF_BYTES) - 2 (not 1 just to be sure it fits)
# * slice_width * 20 (ms per width pixel)
# / 1000 (to transform ms in s) => Approximately 10.88 minutes
MAX_SONG_LENGTH = (2 ** (8 * SLICES_NUMBER_BYTES) - 2) * 128 * 20 / 1000
