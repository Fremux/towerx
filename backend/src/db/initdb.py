from db.session import engine, with_database
from sqlalchemy import exc
from settings import settings
import models
import logging
import chromadb


def create_base_object_classes():
    with with_database() as db:

        chroma_client = chromadb.HttpClient(host=settings.CHROMA_HOST_ADDR, port=settings.CHROMA_HOST_PORT)
        collection = chroma_client.get_or_create_collection(name=settings.CHROMA_DB_NAME)
        all_metadatas = collection.get(include=["metadatas"]).get('metadatas')
        classes_to_create = set([x.get("class") for x in all_metadatas])
        for object_class in classes_to_create:
            try:
                db.add(models.image.ObjectClass(name=object_class,
                                                colour='#FFDC61'))
                db.commit()
            except exc.IntegrityError:
                logging.info(f"{object_class[0]} object class already exists in db")
                db.rollback()
            except Exception as e:
                logging.error(f"{object_class[0]} error while creating object class in db")
                db.rollback()


def create_tables():
    models.base.Base.metadata.create_all(engine)
    create_base_object_classes()
