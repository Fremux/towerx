from db.session import engine, with_database
from sqlalchemy import exc
import models
import logging
from services.chroma import chroma_client

def create_base_object_classes():
    with with_database() as db:
        # all_metadatas = collection.get(include=["metadatas"]).get('metadatas')
        # CLASSES = set([x.get("class") for x in all_metadatas])
        # NUM_CLASSES = len(CLASSES)

        classes_to_create = [('Одноцепная башенного типа', '#7984F1'),
                             ('Двухцепная башенного типа', '#61C6FF'),
                             ('Свободно стоящая типа "рюмка"', '#F179C1'),
                             ('Портальная на оттяжках', '#79F17E'),
                             ('Другие классы', '#FFDC61')]
        for object_class in classes_to_create:
            try:
                db.add(models.image.ObjectClass(name=object_class[0],
                                                colour=object_class[1]))
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
