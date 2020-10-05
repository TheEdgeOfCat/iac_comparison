import json
import logging
import os
from typing import Any, Dict

from edifice_bridge.app import create_app
from edifice_bridge.providers import Providers, create_message_provider
from edifice_bridge.repository import StateRepository


app = create_app()
log = logging.getLogger(__name__)
telegram_provider = create_message_provider(app.config, Providers.TELEGRAM)
twilio_provider = create_message_provider(app.config, Providers.TWILIO)
repository = StateRepository(os.environ['state_dynamodb_table'])


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    log.info(f'Received event: {event}')
    message = telegram_provider.parse_message(event['body'])
    try:
        data: Dict[str, Any] = json.loads(message.text)
        message.source = app.config['message_providers']['twilio']['number']
        message.destination = data['building']
        message.text = data['text']
        twilio_provider.send_message(message)
    except json.decoder.JSONDecodeError:
        active: bool = message.text == 'start'
        repository.put_active(message.source, active)
        message.destination = message.source
        message.text = f'Set active state to {active}'
        telegram_provider.send_message(message)

    return {
        'statusCode': 200,
        'headers': {},
        'isBase64Encoded': False,
        'body': '',
    }
