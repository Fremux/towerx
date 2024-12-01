from sqlalchemy import TIMESTAMP, func, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from typing import List, Dict, Any
from enum import StrEnum
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

apply_image_status = ENUM("completed", "in_progress", "error", "created",
                          name="apply_image_status",
                          metadata=Base.metadata)


class EnumImageStatus(StrEnum):
    completed = "completed"
    in_progress = "in_progress"
    error = "error"
    created = "created"


class Image(Base):
    __tablename__ = "image"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[EnumImageStatus] = mapped_column(apply_image_status,
                                                    server_default=EnumImageStatus.created)
    s3_path: Mapped[str] = mapped_column(nullable=False)
    labeling_data: Mapped[List[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    true_data: Mapped[List[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False,
                                                 server_default=func.current_timestamp())
    validate_id: Mapped[int | None] = mapped_column(ForeignKey("validate.id"), nullable=True)
    is_train: Mapped[bool] = mapped_column(default=False)
    validate: Mapped["Validate"] = relationship(back_populates="images")


class Validate(Base):
    __tablename__ = "validate"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=True)
    date: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False,
                                                 server_default=func.current_timestamp())
    is_finished: Mapped[bool] = mapped_column(server_default="False")
    map_base: Mapped[float] = mapped_column(server_default="0")
    map_50: Mapped[float] = mapped_column(server_default="0")
    map_75: Mapped[float] = mapped_column(server_default="0")
    map_msall: Mapped[float] = mapped_column(server_default="0")
    mar_1: Mapped[float] = mapped_column(server_default="0")
    mar_10: Mapped[float] = mapped_column(server_default="0")
    mar_100: Mapped[float] = mapped_column(server_default="0")
    mar_small: Mapped[float] = mapped_column(server_default="0")
    multiclass_accuracy: Mapped[float] = mapped_column(server_default="0")
    multiclass_f1_score: Mapped[float] = mapped_column(server_default="0")
    multiclass_precision: Mapped[float] = mapped_column(server_default="0")
    multiclass_recall: Mapped[float] = mapped_column(server_default="0")
    iou: Mapped[float] = mapped_column(server_default="0")
    count: Mapped[int] = mapped_column(server_default="0")
    images: Mapped["Image"] = relationship(back_populates="validate")


class ObjectClass(Base):
    __tablename__ = "object_class"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)
    colour: Mapped[str] = mapped_column(nullable=True, server_default="#000000")
