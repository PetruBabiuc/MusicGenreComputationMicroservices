import os

API_HOST = os.getenv('database_api_host', 'localhost')
API_PORT = 2700

API_URL_PREFIX = f'http://{API_HOST}:{API_PORT}'
# RESOURCE_BASE_PATH = '/api/licenta'
RESOURCE_BASE_PATH = ''


# Path parameters names
class PathParamNames:
    USER_ID = 'user_id'
    SERVICE_ID = 'service_id'
    SONG_ID = 'song_id'


# Users
USERS_PATH = f'{RESOURCE_BASE_PATH}/users'
USER_BY_ID_PATH = f'{USERS_PATH}/{{{PathParamNames.USER_ID}}}'
TOGGLE_USER_ACTIVE_PATH = f'{USER_BY_ID_PATH}/toggle-active'

# Identity management
LOGIN_PATH = f'{RESOURCE_BASE_PATH}/login'
LOGOUT_PATH = f'{RESOURCE_BASE_PATH}/logout'
REGISTER_PATH = f'{RESOURCE_BASE_PATH}/register'
VALIDATE_JWT_PATH = f'{RESOURCE_BASE_PATH}/validate-jwt'

# Services
SERVICES_PATH = f'{RESOURCE_BASE_PATH}/services'
USER_BY_ID_SERVICES_PATH = f'{USER_BY_ID_PATH}/services'
USER_BY_ID_SERVICE_BY_ID_PATH = f'{USER_BY_ID_SERVICES_PATH}/{{{PathParamNames.SERVICE_ID}}}'
USER_BILLS = f'{USER_BY_ID_PATH}/bills'

# Songs
SONGS_PATH = f'{RESOURCE_BASE_PATH}/songs'
SONGS_GENRES_PATH = f'{RESOURCE_BASE_PATH}/songs-genres'
SONG_BY_ID_PATH = f'{SONGS_PATH}/{{{PathParamNames.SONG_ID}}}'
SONGS_OF_USER_PATH = f'{USER_BY_ID_PATH}/songs'
EDIT_SONG_PATH = f'{SONG_BY_ID_PATH}/edit'

# Crawler paths
CRAWLER_GENERAL_STATE_BY_ID_PATH = f'{USER_BY_ID_PATH}/crawler'

# Resources urls paths
CRAWLER_RESOURCES_URLS_PATH = f'{CRAWLER_GENERAL_STATE_BY_ID_PATH}/resources-urls'
CRAWLER_RESOURCES_URLS_BULK_ADD_PATH = f'{CRAWLER_RESOURCES_URLS_PATH}/bulk-add'
CRAWLER_RESOURCES_URLS_BULK_DELETE_PATH = f'{CRAWLER_RESOURCES_URLS_PATH}/bulk-delete'
CRAWLER_RESOURCES_URLS_COUNT_PATH = f'{CRAWLER_RESOURCES_URLS_PATH}/count'

# Songs urls paths
SONGS_URLS_PATH = f'{CRAWLER_GENERAL_STATE_BY_ID_PATH}/songs-urls'
SONGS_URLS_COUNT_PATH = f'{SONGS_URLS_PATH}/count'
SONGS_URLS_BULK_ADD_PATH = f'{SONGS_URLS_PATH}/bulk-add'
SONGS_URLS_BULK_DELETE_PATH = f'{SONGS_URLS_PATH}/bulk-delete'

# Bloom filters
BLOOM_FILTER_PATH = f'{CRAWLER_GENERAL_STATE_BY_ID_PATH}/bloom-filter'
