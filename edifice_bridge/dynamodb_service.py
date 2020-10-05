""" DynamoDB AWS service. """
import logging
from typing import Any, Dict, Iterable

import boto3  # type: ignore


log = logging.getLogger(__name__)


class DynamoDBService:
    """ Models a DynamoDB AWS Service. """

    def __init__(self, table) -> None:
        self.table = table
        self.session = boto3.Session()

    @property
    def dynamodb_table(self):
        if hasattr(self, 'connection'):
            return self.connection

        self.connection = self.session.resource('dynamodb').Table(self.table)
        return self.connection

    def scan(self, **kwargs) -> Iterable[Dict[str, Any]]:
        while True:
            response = self.dynamodb_table.scan(**kwargs)
            for item in response.get('Items', []):
                yield item

            kwargs['ExclusiveStartKey'] = response.get(
                'LastEvaluatedKey', None)
            if kwargs['ExclusiveStartKey'] is None:
                break

    def put_item(self, **kwargs) -> Any:
        return self.dynamodb_table.put_item(**kwargs)
