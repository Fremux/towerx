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


