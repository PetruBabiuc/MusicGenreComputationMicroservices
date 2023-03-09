import os
import re

from functional import seq

from functions import stop, start, reset, push_images, create_networks, run_file

replicas = 2
replicated_services = [
    {name: 1 for name in ['maria_db', 'redis', 'rabbit_mq']},
    {'database_api': replicas, 'spectrogram_queue': 1},
    {name: 1 for name in ['song_genre_obtainer', 'genre_computer_request_manager', 'slice_genre_aggregator',
                          'crawler_management_controller', 'song_adder_controller']},
    {
        name: replicas for name in [
            'spider',
            'song_url_processor',
            'crawler_engine',
            'slice_data_processor',
            'slice_genre_predictor',
            'song_validator',
            'spectrogram_filter',
            'spectrogram_maker',
            'spectrogram_slicer'
        ]
    }
]
extern_services = ['redis']

single_replica_services = [list(d.keys()) for d in replicated_services]

images = seq(single_replica_services)\
    .flatten()\
    .filter(lambda it: it not in extern_services)\
    .to_list()

services_creation_commands_file = 'docker_images/service_creation_commands'
with open(services_creation_commands_file) as f:
    networks = list(set(re.findall(r'\w+_network', f.read())))

# Combine outputs:
# docker ps -q | xargs -L 1 -P `docker ps | wc -l` docker logs -n 0 -f
# Delete exited containers:
# docker ps -q -f status=exited | xargs -L 1 -P `docker ps -q -f status=exited | wc -l` docker rm

if __name__ == '__main__':
    services = replicated_services
    stop(services)
    # start(services)
    # reset(services)
    # push_images(images)
    # create_networks(networks)
    # run_file(services_creation_commands_file)
