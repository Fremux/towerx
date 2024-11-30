import logging

from fastapi import APIRouter, Depends, UploadFile
from uuid import uuid4
from typing import List
from db import get_database, Session
from models.image import Image
from schemas.view import GetImage, GetAllImages, ImageLabeling
from services.archive import unpack_archive
from s3 import s3_connection
from rabbitmq import rabbit_connection
from aio_pika import Message, DeliveryMode
from os import path as p
import json
import tempfile
import errors
from settings import settings

router = APIRouter()

SUPPORTED_FILE_TYPES = ["image/jpeg", "image/png", "image/jpg"]
SUPPORTED_ARCHIVE_TYPES = ["application/x-zip-compressed", "application/x-compressed"]


@router.post("/image/upload",
             status_code=201,
             responses=errors.with_errors(errors.unsupported_file_format()))
async def upload_image(files: List[UploadFile],
                       db: Session = Depends(get_database)) -> None:
    """ File upload to system in jpeg, png, jpg, zip, rar and 7z formats"""
    if any(file.content_type not in SUPPORTED_FILE_TYPES + SUPPORTED_ARCHIVE_TYPES for file in files):
        raise errors.unsupported_file_format()
    for file in files:
        if file.content_type in ["image/jpeg", "image/png", "image/jpg"]:
            original_s3_path = f"original/{str(uuid4())}_{file.filename}"
            s3_connection.upload_file(file.file.read(), original_s3_path)
            image = Image(name=file.filename,
                          original_s3_path=original_s3_path)
            db.add(image)
            db.commit()
            message_body = {"id": image.id,
                            "s3_path": original_s3_path}
            message = Message(body=json.dumps(message_body).encode(),
                              content_type="application/json",
                              content_encoding="utf-8",
                              delivery_mode=DeliveryMode.PERSISTENT)
            await rabbit_connection.exchange.publish(message, "analyse")
        else:
            with tempfile.TemporaryDirectory(prefix="transform_") as tmp:
                input_file = tempfile.NamedTemporaryFile(mode="wb+", suffix=f"_{file.filename}", dir=tmp)
                input_file.write(file.file.read())
                input_file.seek(0)
                archive_file_path = p.join(tmp, input_file.name)
                unarchived_files = unpack_archive(archive_file_path, tmp)
                logging.error(unarchived_files)
                logging.error(type(unarchived_files))
                for unarchived_file in unarchived_files:
                    if unarchived_file[0].endswith((".jpg", ".png", ".jpeg")):
                        original_s3_path = f"original/{str(uuid4())}_{unarchived_file[0]}"
                        s3_connection.upload_file(unarchived_file[1].read(), original_s3_path)
                        unarchived_file[1].close()
                        image = Image(name=unarchived_file[0],
                                      original_s3_path=original_s3_path)
                        db.add(image)
                        db.commit()
                        message_body = {"id": image.id,
                                        "s3_path": original_s3_path}
                        message = Message(body=json.dumps(message_body).encode(),
                                          content_type="application/json",
                                          content_encoding="utf-8",
                                          delivery_mode=DeliveryMode.PERSISTENT)
                        await rabbit_connection.exchange.publish(message, "analyse")


@router.get("/image/all",
            response_model=List[GetAllImages],
            responses=errors.with_errors())
async def get_all(db: Session = Depends(get_database)) -> List[GetAllImages]:
    """Get all images base info"""
    images: List[Image] = db.query(Image).order_by(Image.created_at.desc()).all()

    return [GetAllImages(id=image.id,
                         name=image.name,
                         status=image.status,
                         created_at=image.created_at,
                         object_classes=[],
                         preview_s3_url=s3_connection.get_url(image.preview_s3_path)
                         if image.preview_s3_path is not None else None) for image in images]


@router.get("/image/{image_id}/",
            response_model=GetImage,
            responses=errors.with_errors(errors.image_not_found()))
async def get_image_by_id(image_id: int,
                          db: Session = Depends(get_database)) -> GetImage:
    """Get image full info"""
    image = db.query(Image).filter(Image.id == image_id).first()
    if image is None:
        raise errors.image_not_found()
    original_s3_url = s3_connection.get_url(image.original_s3_path)

    return GetImage(id=image.id,
                    name=image.name,
                    status=image.status,
                    labeling=[ImageLabeling(**labeling) for labeling in image.labeling_data]
                    if image.labeling_data is not None else [],
                    created_at=image.created_at,
                    original_s3_url=original_s3_url[original_s3_url.find(settings.AWS_BUCKET):])


@router.delete("/image/{image_id}/",
               status_code=204,
               responses=errors.with_errors())
async def delete_image(image_id: int,
                       db: Session = Depends(get_database)):
    image = db.query(Image).filter(Image.id == image_id).first()
    if image is None:
        raise errors.image_not_found()

    if image.original_s3_path is not None:
        s3_connection.delete_file(image.original_s3_path)
    if image.preview_s3_path is not None:
        s3_connection.delete_file(image.preview_s3_path)

    db.delete(image)
    db.commit()
