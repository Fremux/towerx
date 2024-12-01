import aio_pika
import asyncio
import logging
from io import BytesIO

# from .setting import settings
from connectors.rabbitmq import rabbitmq
from connectors.db import with_database
from connectors.s3 import s3
from schema import ClassifierTask, ListBBoxResult
from classify import classify, add_to_db
from validate import validate
from models import Image, EnumImageStatus, Validate

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
                    if len(task.bboxs):
                        file = BytesIO()
                        s3.download_file(file,"original"+task.s3)
                        result = classify(file, task.bboxs)
                        logger.info(f"Result {result=}")
                    else:
                        logger.info(f"No Bboxes")
                        result = []
                    image:Image = db.query(Image).filter(Image.id == task.id).first()
                    if image is None:
                        logger.error(f"WRONG ID")
                    else:
                        if image.true_data is not None and image.validate is not None and not image.is_train:
                            true_data = ListBBoxResult.model_validate(image.true_data).root
                            logger.info(f"Data to validate {true_data}")
                            metrics = validate(result, true_data)
                            v: Validate = image.validate
                            v.count+=1
                            v.map_50+=metrics.map_50
                            v.map_75+=metrics.map_75
                            v.map_base+=metrics.map_base
                            v.map_msall+=metrics.map_small
                            v.mar_1+=metrics.mar_1
                            v.mar_10+=metrics.mar_10
                            v.mar_100+=metrics.mar_100
                            v.mar_small+=metrics.mar_small
                            v.multiclass_precision += metrics.multiclass_precision
                            v.multiclass_recall += metrics.multiclass_recall
                            v.multiclass_accuracy += metrics.multiclass_accuracy
                            v.multiclass_f1_score += metrics.multiclass_f1_score
                            v.iou+=metrics.iou
                            v.is_finished=True#TODO make check
                            logger.info(f"Update validate")
                        if image.is_train and image.true_data is not None:
                            true_data = ListBBoxResult.model_validate(image.true_data).root
                            logger.info(f"Data to TRAIN {true_data}")
                            file.seek(0)
                            add_to_db(file, true_data)
                        image.status = EnumImageStatus.completed
                        image.labeling_data = result
                    db.commit()
                except ValueError as e:
                    logger.error(f"Cant parse ClassifierTask with error: {e}")
                except FileNotFoundError:
                    image:Image = db.query(Image).filter(Image.id == task.id).first()
                    if image is None:
                        logger.error(f"WRONG ID")
                    else:
                        image.status = EnumImageStatus.error
                    db.commit()
                await message.ack()


if __name__ == "__main__":
    logger.info("Start")
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main(loop))
    loop.close()
