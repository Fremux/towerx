from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional
from schemas.enum import EnumImageStatus


class ImageLabeling(BaseModel):
    label: str
    x: float
    y: float
    w: float
    h: float


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
    preview_s3_url: Optional[str]


class GetObjectClass(BaseModel):
    id: int
    name: str


class ValidationMetrics(BaseModel):
    map_base: float
    map_50: float
    map_75: float
    map_msall: float
    mar_1: float
    mar_10: float
    mar_100: float
    mar_small: float
    multiclass_accuracy: float
    multiclass_f1_score: float
    multiclass_precision: float
    multiclass_recall: float
    iou: float = 0.0


class GetValidationData(BaseModel):
    id: int
    name: str
    created_at: datetime
    is_finished: bool
    metrics: ValidationMetrics
