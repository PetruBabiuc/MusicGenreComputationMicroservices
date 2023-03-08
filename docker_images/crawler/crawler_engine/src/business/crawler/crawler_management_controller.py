import os

HOST = os.getenv('crawler_management_controller_host', 'localhost')

CLIENT_PORT = 1850
CRAWLER_RESPONSES_PORT = 1851

# API Paths
# RESOURCE_BASE_PATH = '/api/licenta'
RESOURCE_BASE_PATH = ''

CRAWLER_PATH = f'{RESOURCE_BASE_PATH}/crawler'
START_CRAWLING_PATH = f'{CRAWLER_PATH}/start-crawling'
CRAWLER_STATUS_PATH = f'{CRAWLER_PATH}/status'
