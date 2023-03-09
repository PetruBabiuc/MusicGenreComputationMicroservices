from __future__ import annotations

import os
import re
import shlex
import subprocess
import time

sleep_time = 10
service_scale_command = 'docker service scale -d '


def get_services() -> list[str]:
    lines = subprocess.check_output(shlex.split('docker service ls')).decode().splitlines()[1:]
    service_regex = re.compile(r'(?<= )\w+')
    result = [service_regex.findall(line)[0] for line in lines]
    return result


def stop(services_collection: list[list[str]] | list[dict[str, int]]) -> None:
    for services in reversed(services_collection):
        if isinstance(services, dict):
            services = services.keys()
        services_to_replicas = ' '.join(f'{s}=0' for s in services)
        os.system(service_scale_command + services_to_replicas)
    time.sleep(sleep_time)


def start(services_collection: list[list[str]] | list[dict[str, int]]) -> None:
    for services in services_collection:
        if isinstance(services, list):
            services = {service: 1 for service in services}
        services_to_replicas = ' '.join(f'{s[0]}={s[1]}' for s in services.items())
        os.system(service_scale_command + services_to_replicas)
        time.sleep(sleep_time)


def reset(services_collection: list[list[str]] | list[dict[str, int]]) -> None:
    stop(services_collection)
    start(services_collection)


def push_images(images: list[str], tag_before_push: bool = False) -> None:
    command = 'docker push petrubabiuc/licenta:{0}'
    if tag_before_push:
        command = 'docker tag localhost:5000/{0} && ' + command
    for image in images:
        os.system(command.format(image))


def create_networks(networks: list[str]) -> None:
    command = 'docker network create -d overlay {0}'
    for network in networks:
        os.system(command.format(network))


def run_file(file_name: str) -> None:
    with open(file_name) as f:
        commands = f.readlines()

    for command in commands:
        if command != '':
            os.system(command)
