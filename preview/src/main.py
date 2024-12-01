import asyncio
import logging
from io import BytesIO

# from .setting import settings
from connectors.rabbitmq import rabbitmq
from connectors.s3 import s3
from schema import PreviewTask
from service import create_preview_image

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
                logger.info(f"Start process {task}")
                create_preview_image(task.s3)
                logger.info("Finished")
            except ValueError as e:
                logger.error(f"Cant parse PreviewTask with error: {e}")
            await message.ack()


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main(loop))
    loop.close()
