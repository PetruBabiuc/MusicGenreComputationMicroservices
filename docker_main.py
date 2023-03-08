import os
import re
import shlex
import subprocess
import time

services_lists = [
    ['maria_db', 'redis', 'rabbit_mq'],
    ['database_api', 'spectrogram_queue'],
    [
        'spider',
        'song_url_processor',
        'song_genre_obtainer',
        'crawler_engine',
        'song_adder_controller',
        'crawler_management_controller',
        'genre_computer_request_manager',
        'slice_data_processor',
        'slice_genre_aggregator',
        'slice_genre_predictor',
        'song_validator',
        'spectrogram_filter',
        'spectrogram_maker',
        'spectrogram_slicer'
    ]
]
sleep_time = 10
service_scale_command = 'docker service scale -d '


def get_services() -> list[str]:
    lines = subprocess.check_output(shlex.split('docker service ls')).decode().splitlines()[1:]
    service_regex = re.compile(r'(?<= )\w+')
    result = [service_regex.findall(line)[0] for line in lines]
    return result


def stop() -> None:
    for services in reversed(services_lists):
        services_to_replicas = ' '.join(f'{s}=0' for s in services)
        os.system(service_scale_command + services_to_replicas)
    time.sleep(sleep_time)


def start() -> None:
    for services in services_lists:
        services_to_replicas = ' '.join(f'{s}=1' for s in services)
        os.system(service_scale_command + services_to_replicas)
        time.sleep(sleep_time)


def reset() -> None:
    stop()
    start()


# Combine outputs:
# docker ps -q | xargs -L 1 -P `docker ps | wc -l` docker logs -n 0 -f
# Delete exited containers:
# docker ps -q -f status=exited | xargs -L 1 -P `docker ps -q -f status=exited | wc -l` docker rm

# TODO: See if 'mariadb.InterfaceError: Lost connection to MySQL' exception still occurs
if __name__ == '__main__':
    stop()
    # reset()
