import json
import logging
from abc import ABCMeta, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from urllib.parse import parse_qs

import requests
from requests.models import Response
from twilio.rest import Client  # type: ignore


log = logging.getLogger(__name__)


class InvalidMessageError(Exception):
    """ Models an error for an invalid received message. """


class Providers(Enum):
    TELEGRAM = 'telegram'
    TWILIO = 'twilio'


class Message():
    """ Models a message object. """

    def __init__(
            self,
            source: str,
            destination: str,
            text: str,
            media: List[str],
            timestamp: Optional[datetime] = None) -> None:
        if not timestamp:
            timestamp = datetime.now()

        self.timestamp: datetime = timestamp
        self.source = source
        self.destination = destination
        self.text = text
        self.media = media

    def __repr__(self):
        return (
            f'Message(text={self.text}, media={self.media}, '
            f'destination={self.destination}, source={self.source}, '
            f'timestamp={self.timestamp.isoformat()})'
        )


class MessageProvider(metaclass=ABCMeta):
    """ Models a Message provider. """

    @abstractmethod
    def send_message(self, message: Message) -> None:
        """ Sends a message. """

    @abstractmethod
    def parse_message(self, raw_message: Any) -> Message:
        """ Parse a received message. """


class TelegramMessageProvider(MessageProvider):
    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config
        self.provider: Providers = Providers.TELEGRAM
        self.bot_token: str = self.config['token']
        self.base_url: str = self.config['base_url'].format(self.bot_token)

    def handle_requests_response(self, r: Response):
        if r.status_code // 100 >= 4:
            if r.headers['Content-Type'] == 'application/json':
                log.error(r.json())
            else:
                log.error(r.content.decode('UTF-8'))

    def send_message(self, message: Message) -> None:
        chat_id: int = int(message.destination)
        text: str = '\n\n'.join([
            message.text,
            *message.media,
        ])
        r: Response = requests.post(f'{self.base_url}/sendMessage', json={
            'chat_id': chat_id,
            'text': text,
        })
        self.handle_requests_response(r)

    def parse_message(self, raw_message: str) -> Message:
        data: Dict[str, Any] = json.loads(raw_message)
        try:
            source: str = str(data['message']['chat']['id'])
            text: str = data['message']['text']
        except KeyError as e:
            raise InvalidMessageError(
                f'Missing parameter "{e.args[0]}" in request data')

        return Message(
            source=source,
            destination='',
            text=text,
            media=[],
        )


class TwilioMessageProvider(MessageProvider):
    def __init__(self, config: Dict[str, Any]) -> None:
        self.provider: Providers = Providers.TWILIO
        self.client = Client(config['sid'], config['token'])

    def send_message(self, message: Message) -> None:
        self.client.messages.create(
            body=message.text,
            media_url=message.media,
            from_=message.source,
            to=message.destination,
        )

    def parse_message(self, raw_message: str) -> Message:
        data: Dict[str, List[str]] = parse_qs(raw_message)
        text = data['Body'][0]
        building = data['From'][0]

        return Message(
            source=building,
            destination='',
            text=text,
            media=[],
        )


def create_message_provider(
        config: Dict[str, Any],
        provider_name: Providers) -> MessageProvider:
    if provider_name == Providers.TELEGRAM:
        return TelegramMessageProvider(
            config['message_providers']['telegram'],
        )
    elif provider_name == Providers.TWILIO:
        return TwilioMessageProvider(
            config['message_providers']['twilio'],
        )
    else:
        raise Exception(
            f'Unknownw provider: {provider_name}'
        )
