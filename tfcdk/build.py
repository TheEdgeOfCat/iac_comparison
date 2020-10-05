import os
import shutil
from typing import Tuple

import docker  # type: ignore


DOCKER_IMAGE_TAG = 'sms_bridge_layer'
LAYER_PACKAGE_DIR = 'dist/layer_package'
LAYER_PACKAGE_FILE = 'dist/dependency_layer'
FUNCTION_PACKAGE_DIR = 'dist/function_package'
FUNCTION_PACKAGE_FILE = 'dist/functions'


def print_log(logs):
    for entry in logs:
        try:
            print(entry['stream'], end='')
        except KeyError:
            pass


def package_layer() -> None:
    layer_package_dir = os.path.join(os.getcwd(), LAYER_PACKAGE_DIR)
    os.makedirs(layer_package_dir, exist_ok=True)
    client = docker.from_env()
    image, logs = client.images.build(path='../', tag=DOCKER_IMAGE_TAG)
    client.containers.run(
        image=image.id,
        remove=True,
        volumes={
            layer_package_dir: {'bind': '/asset-output', 'mode': 'rw'},
        },
    )
    shutil.make_archive(LAYER_PACKAGE_FILE, 'zip', LAYER_PACKAGE_DIR)


def ignore_handler(path, items):
    return set(items) & set(['__pycache__'])


def package_function() -> None:
    os.makedirs(FUNCTION_PACKAGE_DIR, exist_ok=True)
    shutil.copytree(
        '../aws_lambda',
        os.path.join(FUNCTION_PACKAGE_DIR, 'aws_lambda'),
        dirs_exist_ok=True,
        ignore=ignore_handler,
    )
    shutil.copytree(
        '../edifice_bridge',
        os.path.join(FUNCTION_PACKAGE_DIR, 'edifice_bridge'),
        dirs_exist_ok=True,
        ignore=ignore_handler,
    )
    shutil.make_archive(FUNCTION_PACKAGE_FILE, 'zip', FUNCTION_PACKAGE_DIR)


def package_assets() -> Tuple[str, str]:
    package_layer()
    package_function()

    return (
        os.path.join(os.getcwd(), f'{LAYER_PACKAGE_FILE}.zip'),
        os.path.join(os.getcwd(), f'{FUNCTION_PACKAGE_FILE}.zip'),
    )


if __name__ == '__main__':
    package_assets()
