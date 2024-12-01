import aio_pika
import asyncio
import logging
from io import BytesIO

# from .setting import settings
from connectors.rabbitmq import rabbitmq
from connectors.db import with_database
from connectors.s3 import s3
from schema import DetectorTask, ClassifierTask
from detect import detect

logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)


async def main(loop):
    await rabbitmq.connect()
    async with rabbitmq.queue.iterator() as queue_iter:
        logger.info("Start listening for messages")
        async for message in queue_iter:  # async with message.process():
            with with_database() as db:
                logger.info("Process new ClassifierTask")
                try:
                    task = ClassifierTask.model_validate_json(message.body.decode())
                    logger.info(f"Start process {task=}")
                    file = BytesIO()
                    s3.download_file(file,task.s3)
                    result = classify(task)
                    logger.info(f"Result {result=}")
                    
                except ValueError as e:
                    logger.error(f"Cant parse ConnectorTask with error: {e}")
                await message.ack()


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main(loop))
    loop.close()
