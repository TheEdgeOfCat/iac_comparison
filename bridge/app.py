""" An application initializer. """
import logging
import os
from enum import Enum
from typing import Any, Dict

from bridge.configuration import Configuration, load_config
from bridge.logger import initialize_logger


log = logging.getLogger(__name__)


class Environment(Enum):
    """ Defines an application environment. """
    prod = 0
    dev = 1


class App:
    """ Models an application. """

    def __init__(
            self,
            config: Configuration,
            environment: Environment) -> None:
        self._environment = environment
        self._config = config

    @property
    def config(self) -> Dict[str, Any]:
        return self._config.config

    @property
    def environment(self) -> Environment:
        return self._environment


def create_app() -> App:
    """ Initializes an application. """
    app_env = Environment[
        os.environ.get('bridge_env', 'dev')
    ]

    config_path = os.environ.get('bridge_config', None)
    config = load_config(config_path)
    initialize_logger(config.config)

    app: App = App(config, app_env)
    log.info(f'initialized {app_env} environment')

    return app
