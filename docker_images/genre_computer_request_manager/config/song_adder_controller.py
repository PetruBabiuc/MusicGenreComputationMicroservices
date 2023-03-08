import os

HOST = os.getenv('song_adder_controller_host', 'localhost')
CLIENT_PORT = 1800
GENRE_COMPUTATION_PORT = 1801

# API Paths
# RESOURCE_BASE_PATH = '/api/licenta'
RESOURCE_BASE_PATH = ''

# Songs
SONGS_PATH = f'{RESOURCE_BASE_PATH}/songs'
