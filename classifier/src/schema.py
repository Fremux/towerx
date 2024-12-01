from pydantic import BaseModel

class DetectorTask(BaseModel):
    id: int
    s3: str

class Bbox(BaseModel):
    x: float
    y: float
    w: float
    h: float

class ClassifierTask(BaseModel):
    s3: str
    bboxs: list[Bbox]

class BBoxResult(Bbox):
    label: str

class ClassifierResult(BaseModel):
    url: str
    labels: list[BBoxResult]


class ValidationStatistics(BaseModel):
    map_base: float
    map_50: float
    map_75: float
    map_small: float
    mar_1: float
    mar_10: float
    mar_100: float
    mar_small: float
    multiclass_accuracy: float
    multiclass_f1_score: float
    multiclass_precision: float
    multiclass_recall: float