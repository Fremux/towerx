from sqlalchemy import TIMESTAMP, func, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from typing import List, Dict, Any
from models.base import Base, apply_image_status
from schemas.enum import EnumImageStatus


class Image(Base):
    __tablename__ = "image"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[EnumImageStatus] = mapped_column(apply_image_status,
                                                    server_default=EnumImageStatus.created)
    original_s3_path: Mapped[str] = mapped_column(nullable=False)
    preview_s3_path: Mapped[str] = mapped_column(nullable=True)
    labeling_data: Mapped[List[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    true_data: Mapped[List[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False,
                                                 server_default=func.current_timestamp())
    validate_id: Mapped[int | None] = mapped_column(ForeignKey("validate.id"), nullable=True)


class Validate(Base):
    __tablename__ = "validate"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    date: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False,
                                           server_default=func.current_timestamp())
    is_finished: Mapped[bool] = mapped_column(server_default="False")


class ObjectClass(Base):
    __tablename__ = "object_class"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)
    colour: Mapped[str] = mapped_column(nullable=True, server_default="#000000")
