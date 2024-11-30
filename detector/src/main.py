import time

import aio_pika
import asyncio
import logging
from .setting import settings
from connectors.rabbitmq import rabbitmq
from connectors.db import with_database
logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)


async def main(loop):
    await rabbitmq.connect()
    async with rabbitmq.queue.iterator() as queue_iter:
        logger.info("Start listening for messages")
        async for message in queue_iter:  # async with message.process():
            with with_database() as db:
                logger.info("Process new ConnectTask")
                transforms = 0
                documents = []
                error = ""
                try:
                    connector = ConnectTask.model_validate_json(message.body.decode())
                    logger.info(f"Start process {connector=}")
                    documents, error = process(connector)
                    logger.info(f"Processed with {documents=},{error=}")
                except ValueError as e:
                    error = f"Cant parse ConnectorTask with error: {e}"
                if error:
                    logger.error(error)
                    log = ConnectionLog(
                        workflow_id=connector.flow_id,
                        transform_all=0,
                        connection_success=False,
                        error_message=error,
                    )
                else:
                    log = ConnectionLog(
                        workflow_id=connector.flow_id,
                        transform_all=transforms,
                    )
                    if len(transforms) == 0:
                        log.connection_success = True
                db.add(log)
                db.commit()
                try_finish_workflow(connector.flow_id, db)
                for transform in connector.transforms:
                    can = available_types.get(transform.type, [])
                    for document in documents:
                        if document.type in can:
                            transforms += 1
                            logger.info(f"Send {document} to {transform}")
                            exchange_write.publish(
                                aio_pika.Message(
                                    body=TransformTask(
                                        flow_id=connector.flow_id,
                                        document=document,
                                        connector_id=log.id,
                                        type=transform.type,
                                        data=transform.data,
                                        rag_data=connector.rag_data,
                                    )
                                    .model_dump_json()
                                    .encode(),
                                    content_type="application/json",
                                    content_encoding="utf-8",
                                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                                ),
                                "",
                            )
                await message.ack()


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main(loop))
    loop.close()
