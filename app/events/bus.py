
import aio_pika

from .events import AbstractEvent


class EventBus:
    """ Шина событий """

    def __init__(self, channel: aio_pika.channel.AbstractChannel):
        self._channel = channel

    async def publish(self, event: AbstractEvent):
        """ Опубликовать событие """

        await self._channel.default_exchange.publish(
            aio_pika.Message(event.model_dump_json().encode()),
            routing_key=event.routing_key
        )
