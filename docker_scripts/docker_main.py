from functions import stop, start, reset

replicas = 2
replicated_services = [
    {name: 1 for name in ['maria_db', 'redis', 'rabbit_mq']},
    {'database_api': replicas, 'spectrogram_queue': 1},
    {name: 1 for name in ['song_genre_obtainer', 'genre_computer_request_manager', 'slice_genre_aggregator',
                          'crawler_management_controller']},
    {
        name: replicas for name in [
            'spider',
            'song_url_processor',
            'crawler_engine',
            'song_adder_controller',
            'slice_data_processor',
            'slice_genre_predictor',
            'song_validator',
            'spectrogram_filter',
            'spectrogram_maker',
            'spectrogram_slicer'
        ]
    }
]

single_replica_services = [list(d.keys()) for d in replicated_services]

# Combine outputs:
# docker ps -q | xargs -L 1 -P `docker ps | wc -l` docker logs -n 0 -f
# Delete exited containers:
# docker ps -q -f status=exited | xargs -L 1 -P `docker ps -q -f status=exited | wc -l` docker rm

# TODO: See if 'mariadb.InterfaceError: Lost connection to MySQL' exception still occurs
if __name__ == '__main__':
    services = replicated_services
    stop(services)
    # start(services)
    # reset(services)
