import json, requests, torch, supervision as sv, shutil, numpy as np

from pathlib import Path
from io import BytesIO
from schema import Bbox
from tqdm import tqdm
from PIL import Image

from ultralytics import YOLO
from transformers import AutoImageProcessor
from transformers import RTDetrForObjectDetection, RTDetrImageProcessor

def download_file(url, dir, name, chunk_size=8192):
    if not dir.is_dir(): raise ValueError(f"Directory {dir} doesn't exist")

    save_path = dir / name

    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(save_path, "wb") as f:
            for chunk in tqdm(r.iter_content(chunk_size=chunk_size), desc=f"downloading file {name}"):
                f.write(chunk)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")


class DETR():
    def __init__(self, weights):
        if not (".zip" in str(weights)): raise ValueError("model weights must be an archive")
        weight_dir = weights.parent / "DETR"
        if not weight_dir.is_dir(): 
            weight_dir.mkdir(parents=True, exist_ok=True)
            if not weights.is_dir(): shutil.unpack_archive(weights, weight_dir)
        self.model = RTDetrForObjectDetection.from_pretrained(weight_dir, local_files_only=True).to(DEVICE)
        self.processor = AutoImageProcessor.from_pretrained(weight_dir, local_files_only=True)

    def predict(self, image, imgsz=1536):
        inputs = self.processor(image, return_tensors="pt").to(DEVICE)

        with torch.no_grad(): outputs = self.model(**inputs)

        w, h = image.size
        results = self.processor.post_process_object_detection(
            outputs, target_sizes=[(h, w)], threshold=0.2
        )

        detections = sv.Detections.from_transformers(results[0]).with_nms(threshold=0.3)

        detections.class_id = np.zeros_like(detections.class_id)
        detections = detections.with_nms(threshold=0.3)
        labels = ['0'] * len(detections)

        annotated_image = image.copy()
        annotated_image = sv.BoxAnnotator().annotate(annotated_image, detections)
        annotated_image = sv.LabelAnnotator().annotate(annotated_image, detections, labels=labels)

        yolo_annotations = []
        for det in detections:
            xmin, ymin, xmax, ymax = det[0]
            box_width = xmax - xmin
            box_height = ymax - ymin
            x_center = xmin + box_width / 2
            y_center = ymin + box_height / 2

            x_center_norm = x_center / w
            y_center_norm = y_center / h
            width_norm = box_width / w
            height_norm = box_height / h

            yolo_annotations.append([
                str(det[3]), 
                float(x_center_norm),
                float(y_center_norm),
                float(width_norm),
                float(height_norm)
            ])
        return yolo_annotations

class YOLOW(YOLO):
    def predict(self, img, imgsz=1536):
        result = super().predict(img, imgsz=imgsz)
        w, h = img.size

        out = []

        for r in result:
            boxes = r.boxes
            for box in boxes:
                b = box.xyxy[0]
                xmin, ymin, xmax, ymax = b
                box_width = xmax - xmin
                box_height = ymax - ymin
                x_center = xmin + box_width / 2
                y_center = ymin + box_height / 2

                x_center_norm = x_center / w
                y_center_norm = y_center / h
                width_norm = box_width / w
                height_norm = box_height / h
                out.append([box.cls.item(), x_center_norm.item(), y_center_norm.item(), width_norm.item(), height_norm.item()])
        return out

def yolo_to_bbox(result):
    return [Bbox(x=bbx[1], y=bbx[2], w=bbx[3], h=bbx[4]) for bbx in result]


from settings import settings
print(settings.WEIGHTS_DIR)
WEIGHTS_DIR = Path(settings.WEIGHTS_DIR)
MODEL = settings.MODEL
with open(str(WEIGHTS_DIR / "weights.json"), 'r') as file:
    models = json.load(file)

model_c = models[MODEL]


if model_c['type'] != "yolo" and model_c['type'] != "detr": raise ValueError(f"Model type {model_c['tupe']} doesn't supported")

#settings.WEIGHTS_DIR/weights.json

if not (WEIGHTS_DIR / model_c["name"]).exists(): download_file(model_c['url'], WEIGHTS_DIR, model_c["name"])

if model_c['type'] == 'yolo': model = YOLOW(WEIGHTS_DIR / model_c["name"])
else: model = DETR(WEIGHTS_DIR / model_c["name"])


def detect(file: BytesIO) -> list[Bbox]:
    img = Image.open(file)
    result = model.predict(img, imgsz=1536)
    return yolo_to_bbox(result)

if __name__ == "__main__":
    img_url = "https://hb.ru-msk.vkcloud-storage.ru/fits/towers.jpg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=m3KNiQmw9Pfykv3nfBcHyx%2F20241201%2Fru-msk%2Fs3%2Faws4_request&X-Amz-Date=20241201T123155Z&X-Amz-Expires=2591999&X-Amz-SignedHeaders=host&X-Amz-Signature=f2c16d6f24c75e8581c7910a846abf205f7b2b2071d53f847edecff5729a7da8"
    response = requests.get(img_url)
    img_bytes = BytesIO(response.content)

    result = detect(img_bytes)
    print(result)

