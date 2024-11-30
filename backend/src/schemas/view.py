from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional
from schemas.enum import EnumImageStatus


class ImageLabeling(BaseModel):
    object_class: int
    x_center: int
    y_center: int
    width: int
    height: int
    prob: float


class GetAllImages(BaseModel):
    id: int
    name: str
    object_classes: List[str]
    preview_s3_url: Optional[str]
    status: EnumImageStatus
    created_at: datetime


class GetImage(BaseModel):
    id: int
    name: str
    original_s3_url: str
    status: EnumImageStatus
    labeling: List[ImageLabeling]
    created_at: datetime
