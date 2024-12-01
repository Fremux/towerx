from ultralytics import YOLO
from pathlib import Path
from io import BytesIO
from schema import Bbox
import json
# from .settings import settings
# print(settings.WEIGHTS_DIR)
WEIGHTS_DIR = Path("../weights")
MODEL = 0
models = json.load(str(WEIGHTS_DIR / "weights.json"))
model_c = models[MODEL]

(WEIGHTS_DIR / model_c["name"]).is_file()
#settings.WEIGHTS_DIR/weights.json
model = YOLO("path/to/best.pt")  # load a custom model

# Predict with the model
# results = model("https://ultralytics.com/images/bus.jpg")

def detect(file: BytesIO) -> list[Bbox]:
    return [Bbox(x=0.1, y=0.1, w=0.2, h=0.2)]
