from db.session import engine, with_database
import models


def create_tables():
    models.base.Base.metadata.create_all(engine)
