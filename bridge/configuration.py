""" Setups an application configuration. """
import json
import logging
import os
from typing import Any, Dict, Optional

from bridge.fileio.retrieval import get_retrieval_factory


log = logging.getLogger(__name__)

_DEFAULTS = {
    'logger_conf': [
        {
            'level': 'DEBUG',
            'handler': 'stdout',
            'formatter': (
                '%(process)d %(threadName)-10s %(asctime)s'
                ' %(levelname)-7s: %(message)s '
            ),
        },
    ],
    'message_providers': {
        'telegram': {
            'token': '',
            'base_url': 'https://api.telegram.org/bot{}',
        },
        'twilio': {
            'sid': '',
            'token': '',
            'number': '',
        },
    },
}
_CURRENT_DIR_PATH = os.path.abspath(os.path.dirname(__file__))


class Configuration:
    """ Models an application configuration from input dictionary. """

    def __init__(self, init_config: Dict[str, Any]) -> None:
        self._init_conf = dict(init_config)
        self.config = dict(self._init_conf)

    @property
    def config(self) -> Dict[str, Any]:
        return self._config

    @config.setter
    def config(self, new_config: Dict[str, Any]) -> None:
        """ Reloads configuration dictionary. """
        if new_config:
            self._config = dict(new_config)
            log.info('configuration successfully updated')
        else:
            raise ValueError('unable to set empty configuration')

    def reset(self) -> None:
        """ Resets configuration to default. """
        self.config = dict(self._init_conf)

    def update_from_json(self, json_path: str) -> None:
        """ Reloads configuration from input json file. """
        if not os.path.exists(json_path) and not os.path.isfile(json_path):
            raise Exception(f'unable to load conf path {json_path}')
        with open(json_path) as f:
            self.config = json.load(f)


def default_config() -> Configuration:
    """ Returns default configuration. """
    return Configuration(_DEFAULTS)


def load_config(config_path: Optional[str]) -> Configuration:
    """ Loads configuration from path. """
    ret = default_config()
    retrieval_factory = get_retrieval_factory(ret.config)
    if config_path:
        with retrieval_factory.get_retrieval(
                config_path).retrieve(config_path) as downloaded_conf:
            ret.update_from_json(downloaded_conf)
    return ret
