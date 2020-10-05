""" Initializes an application logging. """
import logging
import sys
from logging import Formatter, Handler, StreamHandler
from typing import Any, Dict, Optional


def get_handler(conf: Dict[str, Any]) -> Handler:
    """Create handler from configuration dictionary."""

    log_type = conf['handler']
    ret_handler: Optional[Handler] = None
    formatter = Formatter(conf['formatter'])

    if log_type == 'stdout':
        ret_handler = StreamHandler(sys.stdout)
        ret_handler.setFormatter(formatter)
        ret_handler.setLevel(conf['level'])
    else:
        raise Exception(f'unknown log type {log_type}')

    return ret_handler


def initialize_logger(conf: Dict[str, Any]) -> None:
    """Initializes an application logging."""

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    for handler in list(root.handlers):
        root.removeHandler(handler)

    for logger_conf in conf.get('logger_conf', list()):
        handler = get_handler(logger_conf)
        root.addHandler(handler)
