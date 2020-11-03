import logging
import os
from typing import Any, Dict

from bridge.app import create_app
from bridge.providers import Providers, create_message_provider
from bridge.repository import StateRepository


app = create_app()
log = logging.getLogger(__name__)
telegram_provider = create_message_provider(app.config, Providers.TELEGRAM)
twilio_provider = create_message_provider(app.config, Providers.TWILIO)
repository = StateRepository(os.environ['state_dynamodb_table'])


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    log.info(f'Received event: {event}')
    message = twilio_provider.parse_message(event['body'])
    message.text = f'Building: {message.source}\n\n{message.text}'
    for number in repository.get_active_numbers():
        message.destination = number
        telegram_provider.send_message(message)

    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'isBase64Encoded': False,
        'body': '<Response></Response>',
    }
