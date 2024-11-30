from sqlalchemy import TIMESTAMP, func
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
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False,
                                                 server_default=func.current_timestamp())
