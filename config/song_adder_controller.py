import os

HOST = os.getenv('song_adder_controller_host', 'localhost')
CLIENT_PORT = 1800
GENRE_COMPUTATION_PORT = 1801

SONGS_STORAGE_PATH = 'songs'

# Path parameters names
class PathParamNames:
    SONG_ID = 'song_id'

# API Paths
# RESOURCE_BASE_PATH = '/api/licenta'
RESOURCE_BASE_PATH = ''

# Songs
SONGS_PATH = f'{RESOURCE_BASE_PATH}/songs'
SONG_BY_ID_PATH = f'{SONGS_PATH}/{{{PathParamNames.SONG_ID}}}'
