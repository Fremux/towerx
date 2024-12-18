import logging

from fastapi import APIRouter, Depends, UploadFile
from uuid import uuid4
from typing import List
from db import get_database, Session
from models.image import Image, ObjectClass, Validate
from schemas.view import GetImage, GetAllImages, ImageLabeling, GetObjectClass, GetValidationData, ValidationMetrics
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
SUPPORTED_ARCHIVE_TYPES = ["application/x-zip-compressed", "application/x-compressed", "application/zip"]
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
        if file.content_type in SUPPORTED_FILE_TYPES:
            s3_path = f"/{str(uuid4())}_{file.filename}"
            s3_connection.upload_file(file.file.read(), "original" + s3_path)
            image = Image(name=file.filename,
                          s3_path=s3_path)
            db.add(image)
            db.commit()
            message_body = {"id": image.id,
                            "s3": s3_path}
            message = Message(body=json.dumps(message_body).encode(),
                              content_type="application/json",
                              content_encoding="utf-8",
                              delivery_mode=DeliveryMode.PERSISTENT)
            await rabbit_connection.exchange.publish(message, "")
        else:
            validate = Validate(name=file.filename.split(".")[0])
            db.add(validate)
            with (tempfile.TemporaryDirectory(prefix="transform_") as tmp):
                # Extract data from archive
                input_file = tempfile.NamedTemporaryFile(mode="wb+", suffix=f"_{file.filename}", dir=tmp)
                input_file.write(file.file.read())
                input_file.seek(0)
                archive_file_path = p.join(tmp, input_file.name)
                unarchived_files = unpack_archive(archive_file_path, tmp)
                # Upload and creat tasks for files inside arhcive
                for file_name, file_data in unarchived_files.items():
                    if file_data["image"] is not None:
                        s3_path = f"/{str(uuid4())}_{file_data["image"][0].replace('/','_')}"
                        s3_connection.upload_file(file_data["image"][1].read(), "original" + s3_path)
                        image = Image(name=file_data["image"][0],
                                      s3_path=s3_path,
                                      validate_id=validate.id)
                        if file_data["txt"] is not None:
                            file_data["txt"][1].seek(0)
                            data = file_data["txt"][1].readlines()
                            true_data = []
                            for line in data:
                                label, params = parse_input_file_class(line.decode("utf-8"))
                                labeling_data = {"x": params[0],
                                                 "y": params[1],
                                                 "w": params[2],
                                                 "h": params[3],
                                                 "label": label}
                                true_data.append(labeling_data)
                            image.true_data = true_data
                        db.add(image)
                        db.commit()
                        message_body = {"id": image.id,
                                        "s3": s3_path}
                        message = Message(body=json.dumps(message_body).encode(),
                                          content_type="application/json",
                                          content_encoding="utf-8",
                                          delivery_mode=DeliveryMode.PERSISTENT)
                        await rabbit_connection.exchange.publish(message, "")


@router.get("/image/all",
            response_model=List[GetAllImages],
            responses=errors.with_errors())
async def get_all(db: Session = Depends(get_database)) -> List[GetAllImages]:
    """Get all images base info"""
    images: List[Image] = db.query(Image).order_by(Image.created_at.desc()).all()
    result = []
    for image in images:
        preview_s3_url = s3_connection.get_url("preview" + image.s3_path)
        schema = GetAllImages(id=image.id,
                              name=image.name,
                              status=image.status,
                              created_at=image.created_at,
                              object_classes=[labeling["label"] for labeling in image.labeling_data] if image.labeling_data is not None else [],
                              preview_s3_url=preview_s3_url[preview_s3_url.find(settings.AWS_BUCKET) - 1:] if preview_s3_url is not None else None)
        result.append(schema)

    return result


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
    preview_s3_url = s3_connection.get_url("preview" + image.s3_path)
    return GetImage(id=image.id,
                    name=image.name,
                    status=image.status,
                    labeling=[ImageLabeling(**labeling) for labeling in image.labeling_data]
                    if image.labeling_data is not None else [],
                    created_at=image.created_at,
                    original_s3_url=original_s3_url[original_s3_url.find(settings.AWS_BUCKET) - 1:],
                    preview_s3_url=preview_s3_url[preview_s3_url.find(settings.AWS_BUCKET) - 1:] if preview_s3_url is not None else None)


@router.delete("/image/{image_id}/",
               status_code=204,
               responses=errors.with_errors())
async def delete_image(image_id: int,
                       db: Session = Depends(get_database)):
    image = db.query(Image).filter(Image.id == image_id).first()
    if image is None:
        raise errors.image_not_found()

    if image.s3_path is not None:
        s3_connection.delete_file('original' + image.s3_path)
    if image.s3_path is not None:
        s3_connection.delete_file('preview' + image.s3_path)

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
async def add_object_class(files: list[UploadFile],
                           db: Session = Depends(get_database)) -> None:
    if any(file.content_type not in SUPPORTED_ARCHIVE_TYPES for file in files):
        raise errors.unsupported_file_format()
    classes = set()
    for file in files:
        with (tempfile.TemporaryDirectory(prefix="transform_") as tmp):
            # Extract data from archive
            input_file = tempfile.NamedTemporaryFile(mode="wb+", suffix=f"_{file.filename}", dir=tmp)
            input_file.write(file.file.read())
            input_file.seek(0)
            archive_file_path = p.join(tmp, input_file.name)
            unarchived_files = unpack_archive(archive_file_path, tmp)
            # Upload and creat tasks for files inside arhcive
            for file_name, file_data in unarchived_files.items():
                if file_data["image"] is not None:
                    s3_path = f"/{str(uuid4())}_{file_data["image"][0].replace('/','_')}"
                    s3_connection.upload_file(file_data["image"][1].read(), "original" + s3_path)
                    image = Image(name=file_data["image"][0],
                                    s3_path=s3_path, is_train=True)
                    if file_data["txt"] is not None:
                        file_data["txt"][1].seek(0)
                        data = file_data["txt"][1].readlines()
                        true_data = []
                        for line in data:
                            label, params = parse_input_file_class(line.decode("utf-8"))
                            classes.add(label)
                            labeling_data = {"x": params[0],
                                                "y": params[1],
                                                "w": params[2],
                                                "h": params[3],
                                                "label": label}
                            true_data.append(labeling_data)
                        image.true_data = true_data
                    db.add(image)
                    db.commit()
                    message_body = {"id": image.id,
                                    "s3": s3_path}
                    message = Message(body=json.dumps(message_body).encode(),
                                        content_type="application/json",
                                        content_encoding="utf-8",
                                        delivery_mode=DeliveryMode.PERSISTENT)
                    await rabbit_connection.exchange.publish(message, "")

    for class_name in classes:
        image_name_check = db.query(ObjectClass).filter(ObjectClass.name == class_name).first()
        if image_name_check is None:
            db.add(ObjectClass(name=class_name))
            db.commit()

@router.delete("/class/{object_class_id}/",
               status_code=204,
               responses=errors.with_errors(errors.object_class_not_found()))
async def delete_object_class(object_class_id: int,
                              db: Session = Depends(get_database)) -> None:
    object_class = db.query(ObjectClass).filter(ObjectClass.id == object_class_id).first()
    if object_class is None:
        raise errors.object_class_not_found()
    delete_from_chroma(object_class.name)
    db.delete(object_class)
    db.commit()


@router.get("/validation/all",
            response_model=List[GetValidationData])
async def get_all_validations(db: Session = Depends(get_database)) -> List[GetValidationData]:
    """Get information about batch upload"""
    validations = db.query(Validate).order_by(Validate.date.desc()).all()
    return [GetValidationData(id=validation.id,
                              name=validation.name,
                              created_at=validation.date,
                              is_finished=validation.is_finished,
                              metrics=ValidationMetrics(map_base=validation.map_base/validation.count,
                                                        map_50=validation.map_50/validation.count,
                                                        map_75=validation.map_75/validation.count,
                                                        map_msall=validation.map_msall/validation.count,
                                                        mar_1=validation.mar_1/validation.count,
                                                        mar_10=validation.mar_10/validation.count,
                                                        mar_100=validation.mar_100/validation.count,
                                                        mar_small=validation.mar_small/validation.count,
                                                        multiclass_accuracy=validation.multiclass_accuracy/validation.count,
                                                        multiclass_f1_score=validation.multiclass_f1_score/validation.count,
                                                        multiclass_precision=validation.multiclass_precision/validation.count,
                                                        multiclass_recall=validation.multiclass_recall/validation.count,
                                                        iou=validation.iou/validation.count))
            for validation in validations]
