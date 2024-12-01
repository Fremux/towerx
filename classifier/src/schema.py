from pydantic import BaseModel, RootModel


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
    id: int
    bboxs: list[Bbox]


class BBoxResult(Bbox):
    label: str


class ClassifierResult(BaseModel):
    url: str
    labels: list[BBoxResult]


ListBBoxResult = RootModel[list[BBoxResult]]


class ValidationStatistics(BaseModel):
    map_base: float = 0.0
    map_50: float = 0.0
    map_75: float = 0.0
    map_small: float = 0.0
    mar_1: float = 0.0
    mar_10: float = 0.0
    mar_100: float = 0.0
    mar_small: float = 0.0
    multiclass_accuracy: float=0.0
    multiclass_f1_score: float=0.0
    multiclass_precision: float=0.0
    multiclass_recall: float =0.0
    iou: float = 0.0


zero_stat = ValidationStatistics(
    map_base=0,
    map_50=0,
    map_75=0,
    map_small=0,
    mar_1=0,
    mar_10=0,
    multiclass_accuracy=0,
    multiclass_f1_score=0,
    mar_100=0,
    multiclass_precision=0,
    mar_small=0,
    multiclass_recall=0,
)

one_stat = ValidationStatistics(
    map_base=1,
    map_50=1,
    map_75=1,
    map_small=1,
    mar_1=1,
    mar_10=1,
    multiclass_accuracy=1,
    multiclass_f1_score=1,
    mar_100=1,
    multiclass_precision=1,
    mar_small=1,
    multiclass_recall=1,
    iou=1,
)
