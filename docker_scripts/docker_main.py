from functions import stop, start, reset, push_images, create_networks, run_file
from services_informations import *


# Combine outputs:
# docker ps -q | xargs -L 1 -P `docker ps | wc -l` docker logs -n 0 -f
# Delete exited containers:
# docker ps -q -f status=exited | xargs -L 1 -P `docker ps -q -f status=exited | wc -l` docker rm

if __name__ == '__main__':
    services = replicated_services

    # stop(services)
    # stop(services[1:])  # Stop all the services besides the one used to run in debug mode, on localhost with main.py

    # start(services)
    # start([services[0]])  # Start services necessary for running in the debug mode, on localhost with main.py

    reset(services)

    # push_images(images)
    # create_networks(networks)
    # run_file(services_creation_commands_file)
