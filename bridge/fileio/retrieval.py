""" Resource retrievals from various sources. """
import logging
import os
from abc import ABCMeta, abstractmethod
from contextlib import contextmanager
from tempfile import TemporaryDirectory
from typing import Any, Dict, Generator, Optional

from bridge.fileio.path import PathType, S3Path, get_path_type
from bridge.s3_service import S3Service, create_s3_service


log = logging.getLogger(__name__)


class UnknownRetrievalTypeError(ValueError):
    """ Models an error for unknown retrieval type. """


class FileRetrieval(metaclass=ABCMeta):
    """ Models a file downloader. """

    @contextmanager
    def retrieve(
            self, input_path: str) -> Generator[str, None, None]:
        """ Downloads file and returns updated video metadata. """
        ret: str = self.download(input_path)
        yield ret
        self.remove_copy(ret)

    @abstractmethod
    def download(self, input_path: str) -> str:
        """ Gets a file and returns it's path. """

    @abstractmethod
    def remove_copy(self, input_path: str) -> None:
        """ Remove used copy file. """


class LocalFileRetrieval(FileRetrieval):
    """ Models a local file loader. """

    def download(self, input_path: str) -> str:
        """ Returns the same input path. """
        return input_path

    def remove_copy(self, input_path) -> None:
        """ Does nothing since we use local file system. """
        return None


class S3FileRetrieval(FileRetrieval):
    """ Models a S3 file downloader. """

    def __init__(self, s3_service: S3Service) -> None:
        super().__init__()
        self.s3_service = s3_service
        self.tmp_dir = TemporaryDirectory()

    def __del__(self) -> None:
        self.tmp_dir.cleanup()

    def download(self, input_path: str) -> str:
        """ Downloadsfrom the S3 and returns a local path of the file. """
        s3_path = S3Path(input_path)
        filename = os.path.basename(s3_path.key)
        out_path = os.path.join(self.tmp_dir.name, filename)
        log.info(f'downloading file from {input_path} to {out_path}')
        self.s3_service.client.download_file(
            Bucket=s3_path.bucket_name,
            Key=s3_path.key,
            Filename=out_path)
        log.info(
            f'finished download {input_path} to {out_path}')
        return out_path

    def remove_copy(self, input_path: str) -> None:
        """ Removes downloaded copy of the file. """
        os.remove(input_path)
        log.info(f'removed file {input_path}')


class RetrievalFactory:
    """ Models a retrieval factory for file download. """

    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config

    def get_retrieval(self, input_path: str) -> FileRetrieval:
        """ Returns a retrieval based in input path type. """
        path_type = get_path_type(input_path)
        ret: Optional[FileRetrieval] = None
        if path_type == PathType.local:
            ret = LocalFileRetrieval()
        elif path_type == PathType.s3:
            ret = S3FileRetrieval(create_s3_service(self.config))
        else:
            raise UnknownRetrievalTypeError(
                f'unable to instantiate {path_type} retrieval')

        return ret


def get_retrieval_factory(config: Dict[str, Any]) -> RetrievalFactory:
    """ Returns retrieval factory. """
    return RetrievalFactory(config)
