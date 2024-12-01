from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import declarative_base

Base = declarative_base()

apply_image_status = ENUM("completed", "in_progress", "error", "created",
                          name="apply_image_status",
                          metadata=Base.metadata)
