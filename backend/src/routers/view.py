import logging

from fastapi import APIRouter, Depends, UploadFile
from uuid import uuid4
from typing import List
from db import get_database, Session
from models.image import Image, ObjectClass, Validate
from schemas.view import GetImage, GetAllImages, ImageLabeling, GetObjectClass
from services.archive import unpack_archive
from services.chroma import delete_from_chroma, insert_class_to_chroma, parse_input_file_class
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
SUPPORTED_TXT_FILES = []


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
            validate = Validate()
            db.add(validate)
            with tempfile.TemporaryDirectory(prefix="transform_") as tmp:
                input_file = tempfile.NamedTemporaryFile(mode="wb+", suffix=f"_{file.filename}", dir=tmp)
                input_file.write(file.file.read())
                input_file.seek(0)
                archive_file_path = p.join(tmp, input_file.name)
                unarchived_files = unpack_archive(archive_file_path, tmp)

                for unarchived_file in unarchived_files:
                    if unarchived_file[0].endswith((".jpg", ".png", ".jpeg")):
                        s3_path = f"/{str(uuid4())}_{unarchived_file[0]}"
                        s3_connection.upload_file(unarchived_file[1].read(), "original" + original_s3_path)
                        unarchived_file[1].close()
                        image = Image(name=unarchived_file[0],
                                      s3_path=s3_path,
                                      validate_id=validate.id)
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
                         preview_s3_url=s3_connection.get_url("original" + image.s3_path)) for image in images]


@router.get("/image/{image_id}/",
            response_model=GetImage,
            responses=errors.with_errors(errors.image_not_found()))
async def get_image_by_id(image_id: int,
                          db: Session = Depends(get_database)) -> GetImage:
    """Get image full info"""
    image = db.query(Image).filter(Image.id == image_id).first()
    if image is None:
        raise errors.image_not_found()
    original_s3_url = s3_connection.get_url("original" + image.s3_path)

    return GetImage(id=image.id,
                    name=image.name,
                    status=image.status,
                    labeling=[ImageLabeling(**labeling) for labeling in image.labeling_data]
                    if image.labeling_data is not None else [],
                    created_at=image.created_at,
                    original_s3_url=original_s3_url[original_s3_url.find(settings.AWS_BUCKET)-1:])


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


@router.get("/class/all",
            response_model=List[GetObjectClass],
            responses=errors.with_errors())
async def get_all_object_classes(db: Session = Depends(get_database)) -> List[GetObjectClass]:
    object_classes = db.query(ObjectClass).all()
    return [GetObjectClass(id=object_class.id,
                           name=object_class.name) for object_class in object_classes]


@router.post("/class/create",
             status_code=201,
             responses=errors.with_errors(errors.object_class_already_exists()))
async def add_object_class(file: UploadFile,
                           db: Session = Depends(get_database)) -> None:
    class_names, embeddings = [], []
    for line in file.file.readlines():
        class_name, embedding = parse_input_file_class(line)
        image_name_check = db.query(ObjectClass).filter(ObjectClass.name == class_name).first()
        class_names.append(class_name)
        embeddings.append(embeddings)
        if image_name_check is None:
            db.add(ObjectClass(name=class_name))
            db.flush()
        else:
            db.rollback()
            raise errors.object_class_already_exists()
    db.commit()
    insert_class_to_chroma(class_names, embeddings)


@router.delete("/class/delete",
               status_code=204,
               responses=errors.with_errors(errors.object_class_not_found()))
async def delete_object_class(object_class_id: int,
                              db: Session = Depends(get_database)) -> None:
    object_class = db.query(ObjectClass).filter(ObjectClass.id == object_class_id).first()
    if object_class is None:
        raise errors.object_class_not_found()
    db.delete(object_class)
    db.commit()
    delete_from_chroma(object_class_id)
