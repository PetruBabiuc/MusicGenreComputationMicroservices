import json
import os
from threading import Thread

docker_registry = 'petrubabiuc/licenta'


def build_image(image_name: str, path: str) -> None:
    os.system(f'docker build -t {docker_registry}:{image_name} -f {path}/Dockerfile .')


if __name__ == '__main__':
    with open('docker_scripts/images.json') as f:
        images = json.load(f)
    threads = [Thread(target=build_image, args=(it['name'], it['path'])) for it in images]

    for t in threads:
        t.start()

    for t in threads:
        t.join()
