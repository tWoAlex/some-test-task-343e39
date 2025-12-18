import asyncio
from asyncio.exceptions import CancelledError

import aio_pika

from app.events.events import NewOrder
from app.celery.main import process_order


class NewOrderMessageConsumer:
    """ Консьюмер сообщений о новых заказах """

    def __init__(self, channel: aio_pika.channel.AbstractChannel):
        self._channel = channel

    async def consume_process(self, queue: aio_pika.queue.AbstractQueue):
        """ Корутина обработки сообщений """

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    new_order_message = NewOrder.model_validate_json(message.body)
                    print(f"Found new order with id <{new_order_message.order_data.id}>")

                    loop = asyncio.get_running_loop()
                    await loop.run_in_executor(
                        None,
                        process_order.delay,
                        new_order_message.order_data.id
                    )

    async def start_consuming(self):
        """ Начать обработку сообщений """

        await self._channel.set_qos(prefetch_count=5)
        queue = await self._channel.get_queue('new_order')
        try:
            await self.consume_process(queue)
        except CancelledError:
            await self._channel.close()
