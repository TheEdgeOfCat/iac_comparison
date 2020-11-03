from typing import Iterable

from boto3.dynamodb.conditions import Attr

from bridge.dynamodb_service import DynamoDBService


class StateRepository():
    def __init__(self, table_name: str) -> None:
        self.table_name = table_name
        self.dynamodb = DynamoDBService(self.table_name)

    def get_active_numbers(self) -> Iterable[str]:
        items = self.dynamodb.scan(FilterExpression=Attr('active').eq(True))
        for item in items:
            yield item['user_number']

    def put_active(self, user_number: str, active: bool) -> None:
        self.dynamodb.put_item(Item={
            'user_number': user_number,
            'active': active,
        })
