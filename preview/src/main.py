import aio_pika
import asyncio
import logging
from io import BytesIO

# from .setting import settings
from connectors.rabbitmq import rabbitmq
from connectors.s3 import s3
from schema import PreviewTask

logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)


async def main(loop):
    await rabbitmq.connect()
    async with rabbitmq.queue.iterator() as queue_iter:
        logger.info("Start listening for messages")
        async for message in queue_iter:  # async with message.process():
                logger.info("Process new PreviewTask")
                try:
                    task = PreviewTask.model_validate_json(message.body.decode())
                    logger.info(f"Start process {task=}")
                    file = BytesIO()
                    s3.download_file(file,task.s3)
                    #TODO make preview
                    logger.info(f"Finished")
                except ValueError as e:
                    logger.error(f"Cant parse PreviewTask with error: {e}")
                await message.ack()


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main(loop))
    loop.close()
