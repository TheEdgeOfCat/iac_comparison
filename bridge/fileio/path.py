""" Input path parser. """
import logging
from enum import Enum
from typing import Optional
from urllib.parse import urlparse


log = logging.getLogger(__name__)


class UnknownPathTypeError(TypeError):
    """ Models a unknown path type exceptions. """


class PathType(Enum):
    """ Models a possible path types. """
    local = 0
    file = 0
    s3 = 1


class S3Path:
    """ Models a S3 type path parser. """

    def __init__(self, input_path: str) -> None:
        self.full_path = input_path
        self.parsed_path = urlparse(input_path)

    @property
    def bucket_name(self) -> str:
        return self.parsed_path.netloc

    @property
    def key(self) -> str:
        ret = self.parsed_path.path
        if ret.startswith('/'):
            ret = ret[1:]
        return ret


def get_path_type(path: str) -> PathType:
    """ Returns a path type from input path. """
    ret: Optional[PathType] = None
    if not path:
        raise UnknownPathTypeError('not existing path')
    parsed_path = urlparse(path)

    if parsed_path.scheme == '':
        ret = PathType.local
    else:
        try:
            ret = PathType[parsed_path.scheme]
        except KeyError:
            raise UnknownPathTypeError(
                f'unknown path type {parsed_path.scheme}')
    log.debug(f'path {path} is {ret} type')
    return ret
