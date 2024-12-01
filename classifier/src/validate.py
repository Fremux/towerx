from schema import BBoxResult, ValidationStatistics
from torchmetrics import Metric, Accuracy, AUROC, F1Score, Precision, Recall
from torchmetrics.detection.mean_ap import MeanAveragePrecision
from typing import List, Dict
from torch import Tensor
from random import random

import os, chromadb, torch


CHROMADB_URL = os.getenv("CHROMADB_URL", "62.169.159.176")
CHROMADB_PORT = os.getenv("CHROMADB_PORT", "28001")
CHROMADB_NAME = os.getenv("CHROMADB_NAME", "towers")

client = chromadb.HttpClient(host=CHROMADB_URL, port=int(CHROMADB_PORT))
collection = client.get_or_create_collection(CHROMADB_NAME)

def box_to_tensor(data: List[BBoxResult]):
    result = []
    for i in data:
        t = Tensor([i.x, i.y, i.w, i.h])
        result.append(t)
    return torch.stack(result)

def label_to_tensor(labels: List[str], reverse_class_maper: Dict[str, int]):
    return torch.stack([Tensor([reverse_class_maper[i.label]]).to(torch.int16) for i in labels]).squeeze()

def validate(predict: list[BBoxResult], true_label: list[BBoxResult]) -> ValidationStatistics:
    all_metadatas = collection.get(include=["metadatas"]).get('metadatas')
    CLASSES = set([x.get("class") for x in all_metadatas])
    NUM_CLASSES = len(CLASSES)

    reverse_class_maper = {string: i for i, string in enumerate(CLASSES)}

    map = MeanAveragePrecision(box_format="xywh")
    acc = Accuracy(task="multiclass", num_classes=NUM_CLASSES)
    f1 = F1Score(task="multiclass", num_classes=NUM_CLASSES)
    prec = Precision(task="multiclass", num_classes=NUM_CLASSES)
    rec = Recall(task="multiclass", num_classes=NUM_CLASSES)

    preds = [
        {
            "boxes": box_to_tensor(predict),
            "scores": torch.randn(len(predict)), # for iou, skip
            "labels": label_to_tensor(predict, reverse_class_maper), # for iou, skip
        }
    ]

    gt = [
        {
            "boxes": box_to_tensor(true_label),
            "scores": torch.randn(len(true_label)), # for iou, skip
            "labels": label_to_tensor(true_label, reverse_class_maper), # for iou, skip
        }
    ]
    metrics = map(preds, gt)
    metrics['accuracy'] = acc(preds[0]['labels'], gt[0]['labels'])
    metrics['F1-score'] = f1(preds[0]['labels'], gt[0]['labels'])
    metrics["Precision"] = prec(preds[0]['labels'], gt[0]['labels'])
    metrics["Recall"] = rec(preds[0]['labels'], gt[0]['labels'])

    metrics.pop("map_medium")
    metrics.pop("map_large")
    metrics.pop("mar_medium")
    metrics.pop("mar_large")
    metrics.pop("map_per_class")
    metrics.pop("mar_100_per_class")
    metrics.pop("classes")

    result = ValidationStatistics(
        map_base=metrics['map'],
        map_50=metrics['map_50'],
        map_75=metrics['map_75'],
        map_small=metrics['map_small'],
        mar_1=metrics['mar_1'],
        mar_10=metrics["mar_10"],
        mar_100=metrics['mar_100'],
        mar_small=metrics['mar_small'],
        multiclass_accuracy=metrics['accuracy'],
        multiclass_f1_score=metrics['F1-score'],
        multiclass_precision=metrics['Precision'],
        multiclass_recall=metrics['Recall']
    )

    return result

if __name__ == "__main__":
    pred = [
        BBoxResult(
            label="Двухцепная башенного типа",
            x=0.1902890625, #+ random() * 0.1,
            y=0.3348229166666667 ,#+ random() * 0.1,
            w=0.08817187500000001,#+ random() * 0.1,
            h=0.38690624999999995,#+ random() * 0.1
        ),
        BBoxResult(
            label="Двухцепная башенного типа",
            x=0.5357109375 + random() * 0.1,
            y=0.29464583333333333+ random() * 0.1,
            w=0.13616406249999996+ random() * 0.1,
            h=0.4047604166666666+ random() * 0.1
        ),
        BBoxResult(
            label="Одноцепная башенного типа",
            x=0.490515625 + random() * 0.1,
            y= 0.42634375+ random() * 0.1,
            w=0.04129687499999992+ random() * 0.1,
            h=0.12351041666666672+ random() * 0.1
        )
    ]

    gt = [
        BBoxResult(
            label="Двухцепная башенного типа",
            x=0.1902890625, #+ random() * 0.1,
            y=0.3348229166666667 ,#+ random() * 0.1,
            w=0.08817187500000001,#+ random() * 0.1,
            h=0.38690624999999995,#+ random() * 0.1
        ),
        BBoxResult(
            label="Двухцепная башенного типа",
            x=0.5357109375 ,
            y=0.29464583333333333,
            w=0.13616406249999996,
            h=0.4047604166666666
        ),
        BBoxResult(
            label="Одноцепная башенного типа",
            x=0.490515625,
            y= 0.42634375,
            w=0.04129687499999992,
            h=0.12351041666666672
        )
    ]
    print(validate(pred, gt))