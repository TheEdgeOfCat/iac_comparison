""" An application initializer. """
import logging
import os
from enum import Enum
from typing import Any, Dict

from edifice_bridge.configuration import Configuration, load_config
from edifice_bridge.logger import initialize_logger


log = logging.getLogger(__name__)


class Environment(Enum):
    """ Defines an application environment. """
    PROD = 0
    DEV = 1
    TEST = 2


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
        os.environ.get('edifice_bridge_env', 'DEV')
    ]

    config_path = os.environ.get('edifice_bridge_config', None)
    config = load_config(config_path)
    initialize_logger(config.config)

    app: App = App(config, app_env)
    log.info(f'initialized {app_env} environment')

    return app
