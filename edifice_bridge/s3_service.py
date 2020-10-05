import logging
from functools import wraps
from typing import Any, Dict

import boto3


log = logging.getLogger(__name__)


class S3Service:
    """ Models a S3 service client. """

    def __init__(self, conf: Dict[str, Any]) -> None:
        self.conf = dict(conf)
        self.session = boto3.Session()

    @property
    def client(self):
        ret = self.session.client('s3')
        return ret


def cache_connection(func):
    connection = None

    @wraps(func)
    def _create(settings):
        nonlocal connection
        ret = None
        if connection:
            ret = connection
        else:
            ret = func(settings)
            connection = ret
        return ret
    return _create


@cache_connection
def create_s3_service(conf: Dict[str, Any]) -> S3Service:
    return S3Service(conf)
