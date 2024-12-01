from pydantic import BaseModel


class PreviewTask(BaseModel):
    id: int
    s3: str
